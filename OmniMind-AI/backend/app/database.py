"""
Database connection handling for OmniMind AI.
Connects to MySQL 8.0 with PyMySQL, with graceful SQLite fallback for offline development/testing.
Provides parameterized SQL execution methods.
"""

import logging
import sqlite3
from typing import Any, Dict, List, Optional, Tuple
import pymysql
from pymysql.cursors import DictCursor

from .config import settings
from .models.models import (
    MYSQL_TABLE_SCHEMAS,
    SQLITE_TABLE_SCHEMAS,
    DEFAULT_USER_SQL,
    DEFAULT_USER_SQLITE
)

logger = logging.getLogger("omnimind.database")


class DatabaseManager:
    def __init__(self):
        self.is_mysql: bool = False
        self.mysql_pool = None
        self.sqlite_conn: Optional[sqlite3.Connection] = None
        self.db_type: str = "unknown"
        self._initialized: bool = False

    def init_db(self):
        """Attempts to connect to MySQL 8.0, otherwise initializes fallback SQLite."""
        if self._initialized:
            return

        try:
            logger.info("Connecting to MySQL at %s:%s...", settings.MYSQL_HOST, settings.MYSQL_PORT)
            # Try to connect without DB first to ensure DB exists
            admin_conn = pymysql.connect(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                cursorclass=DictCursor,
                connect_timeout=3
            )
            with admin_conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{settings.MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            admin_conn.commit()
            admin_conn.close()

            # Now connect to target database
            test_conn = self._get_mysql_connection()
            with test_conn.cursor() as cursor:
                for schema_sql in MYSQL_TABLE_SCHEMAS:
                    cursor.execute(schema_sql)
                cursor.execute(DEFAULT_USER_SQL)
            test_conn.commit()
            test_conn.close()

            self.is_mysql = True
            self.db_type = "MySQL 8.0"
            self._initialized = True
            logger.info("Successfully connected and initialized MySQL 8.0 database '%s'.", settings.MYSQL_DATABASE)
            return

        except Exception as e:
            logger.warning(
                "MySQL 8.0 connection failed (%s). Falling back to SQLite local database for development/testing.",
                e
            )
            self._init_sqlite()

    def _init_sqlite(self):
        """Initializes a local SQLite database for standalone execution and automated tests."""
        self.is_mysql = False
        self.db_type = "SQLite (Mock/Fallback Mode)"
        db_path = "omnimind_local.db"
        self.sqlite_conn = sqlite3.connect(db_path, check_same_thread=False)
        self.sqlite_conn.row_factory = sqlite3.Row
        with self.sqlite_conn:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            for schema_sql in SQLITE_TABLE_SCHEMAS:
                cursor.execute(schema_sql)
            cursor.execute(DEFAULT_USER_SQLITE)
        self._initialized = True
        logger.info("Initialized local fallback database '%s'.", db_path)

    def _get_mysql_connection(self):
        return pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DATABASE,
            cursorclass=DictCursor,
            autocommit=True
        )

    def execute_insert(self, query: str, params: Tuple = ()) -> int:
        """Executes INSERT query with parameterized arguments and returns lastrowid."""
        if not self._initialized:
            self.init_db()

        if self.is_mysql:
            conn = self._get_mysql_connection()
            try:
                with conn.cursor() as cursor:
                    # Convert ? placeholders to %s for MySQL if needed
                    formatted_query = query.replace("?", "%s")
                    cursor.execute(formatted_query, params)
                    return cursor.lastrowid
            finally:
                conn.close()
        else:
            with self.sqlite_conn:
                cursor = self.sqlite_conn.cursor()
                formatted_query = query.replace("%s", "?")
                cursor.execute(formatted_query, params)
                return cursor.lastrowid

    def execute_query(self, query: str, params: Tuple = ()) -> int:
        """Executes UPDATE/DELETE queries with parameterized arguments and returns affected rows."""
        if not self._initialized:
            self.init_db()

        if self.is_mysql:
            conn = self._get_mysql_connection()
            try:
                with conn.cursor() as cursor:
                    formatted_query = query.replace("?", "%s")
                    cursor.execute(formatted_query, params)
                    return cursor.rowcount
            finally:
                conn.close()
        else:
            with self.sqlite_conn:
                cursor = self.sqlite_conn.cursor()
                formatted_query = query.replace("%s", "?")
                cursor.execute(formatted_query, params)
                return cursor.rowcount

    def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Fetches all rows as a list of dictionaries."""
        if not self._initialized:
            self.init_db()

        if self.is_mysql:
            conn = self._get_mysql_connection()
            try:
                with conn.cursor() as cursor:
                    formatted_query = query.replace("?", "%s")
                    cursor.execute(formatted_query, params)
                    return cursor.fetchall()
            finally:
                conn.close()
        else:
            cursor = self.sqlite_conn.cursor()
            formatted_query = query.replace("%s", "?")
            cursor.execute(formatted_query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetches single row as a dictionary."""
        if not self._initialized:
            self.init_db()

        if self.is_mysql:
            conn = self._get_mysql_connection()
            try:
                with conn.cursor() as cursor:
                    formatted_query = query.replace("?", "%s")
                    cursor.execute(formatted_query, params)
                    return cursor.fetchone()
            finally:
                conn.close()
        else:
            cursor = self.sqlite_conn.cursor()
            formatted_query = query.replace("%s", "?")
            cursor.execute(formatted_query, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_status(self) -> Dict[str, Any]:
        """Returns database status for health check."""
        try:
            row = self.fetch_one("SELECT 1 as alive")
            return {
                "connected": row is not None and row.get("alive") == 1,
                "type": self.db_type,
                "is_mysql": self.is_mysql
            }
        except Exception as e:
            return {
                "connected": False,
                "type": self.db_type,
                "error": str(e)
            }


db = DatabaseManager()
