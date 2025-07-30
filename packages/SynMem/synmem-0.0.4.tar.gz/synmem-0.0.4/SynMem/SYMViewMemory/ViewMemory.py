import os
import sqlite3
import logging

logger = logging.getLogger(__name__)


class ViewMemory:
    def __init__(self, dbLock):
        self.dbLock = dbLock

    def viewDatabase(self, dbPath, limit=None):
        return self._viewTable(dbPath, "memory", limit)

    def viewDetailsDatabase(self, dbPath, limit=None):
        return self._viewTable(dbPath, "memory", limit)

    def _viewTable(self, dbPath, tableName, limit=None):
        if not os.path.exists(dbPath):
            logger.warning(f"Database not found: {dbPath}")
            return []

        try:
            with self.dbLock, sqlite3.connect(dbPath) as conn:
                cursor    = conn.cursor()

                # Check if table exists
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tableName}'")
                if not cursor.fetchone():
                    logger.warning(f"No '{tableName}' table in: {dbPath}")
                    return []

                cursor.execute(f"PRAGMA table_info({tableName})")
                columns = [col[1] for col in cursor.fetchall()]

                query = f"SELECT * FROM {tableName}"
                if limit:
                    query += f" ORDER BY id DESC LIMIT {limit}"

                cursor.execute(query)
                rows       = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            logger.error(f"[Viewer] Error reading {dbPath}:", exc_info=True)
            return []
