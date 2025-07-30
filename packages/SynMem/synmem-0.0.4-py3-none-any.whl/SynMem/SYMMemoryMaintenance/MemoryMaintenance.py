import os
import time
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MemoryMaintenance:
    def __init__(self, dbLock, dbPaths, getTimedeltaFunc, createPersonalDatabase, createMemoryDatabase, createDetailsDatabase):
        self.dbLock                 = dbLock
        self.db                     = dbPaths
        self.getTimedelta           = getTimedeltaFunc
        self.createPersonalDatabase = createPersonalDatabase
        self.createMemoryDatabase   = createMemoryDatabase
        self.createDetailsDatabase  = createDetailsDatabase

    def getDir(self, *paths):
        return str(Path(*paths).resolve())

    def checkDatabases(self, sourceDir, timeCheckFunc, actionFunc, expireDelta):
        for root, _, files in os.walk(sourceDir, topdown=False):
            for file in files:
                try:
                    dbFile   = self.getDir(root, file)
                    fileTime = timeCheckFunc(dbFile)
                    if datetime.now() - fileTime > expireDelta:
                        actionFunc(dbFile, file)
                except Exception as e:
                    logger.error(f"Error processing {file}:", exc_info=True)

    def moveDatabase(self, srcFile, destFile, createQuery, selectQuery, insertQuery):
        os.makedirs(os.path.dirname(destFile), exist_ok=True)

        # Ensure destination has table
        with self.dbLock, sqlite3.connect(destFile) as destConn:
            destCursor = destConn.cursor()
            destCursor.execute(createQuery)
            destConn.commit()

        try:
            with self.dbLock, sqlite3.connect(srcFile) as srcConn:
                srcCursor = srcConn.cursor()

                # Verify source table exists
                srcCursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory'")
                if not srcCursor.fetchone():
                    logger.warning(f"Skipping '{srcFile}' - no memory table.")
                    return

                srcCursor.execute(selectQuery)
                rows = srcCursor.fetchall()

                with sqlite3.connect(destFile) as destConn:
                    destCursor = destConn.cursor()
                    destCursor.executemany(insertQuery, rows)
                    destConn.commit()

                srcCursor.execute("PRAGMA table_info(memory)")
                columns = [col[1] for col in srcCursor.fetchall()]
                hasUser = "user" in columns

                if hasUser:
                    srcCursor.executemany(
                        "DELETE FROM memory WHERE user = ? AND dtStamp = ?",
                        [(row[0], row[1]) for row in rows]
                    )
                else:
                    srcCursor.executemany(
                        "DELETE FROM memory WHERE dtStamp = ?",
                        [(row[0],) for row in rows]
                    )

        except sqlite3.OperationalError as e:
            logger.error(f"OperationalError moving '{srcFile}':", exc_info=True)
        except Exception as e:
            logger.error(f"Unexpected error moving '{srcFile}':", exc_info=True)

    # ========== Expiration Actions ==========

    def removeOldSensory(self, expireUnit, expireValue):
        self.checkDatabases(
            self.db.senDir,
            lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
            lambda dbFile, file: os.remove(dbFile),
            self.getTimedelta(expireUnit, expireValue)
        )

    def removeOldInteractionDetails(self, expireUnit, expireValue):
        self.checkDatabases(
            self.db.stmUserInteractionDetails,
            lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
            lambda dbFile, file: os.remove(dbFile),
            self.getTimedelta(expireUnit, expireValue)
        )

    def removeOldImageDetails(self, expireUnit, expireValue):
        self.checkDatabases(
            self.db.stmCreatedImageDetails,
            lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
            lambda dbFile, file: os.remove(dbFile),
            self.getTimedelta(expireUnit, expireValue)
        )

    def removeOldConversationDetails(self, expireUnit, expireValue):
        dbPath = self.getDir(self.db.stmDir, "STM.db")
        expireThreshold = datetime.now() - self.getTimedelta(expireUnit, expireValue)

        if not os.path.exists(dbPath):
            return

        try:
            with self.dbLock, sqlite3.connect(dbPath) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM memory WHERE dtStamp <= ?",
                    (expireThreshold.isoformat(),)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to remove old STM records:", exc_info=True)


    # ========== Archive Actions ==========

    def archiveConversationDetails(self, expireUnit, expireValue):
        self.checkDatabases(
            self.db.stmUserConversationDetails,
            lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
            self.moveConversationDetails,
            self.getTimedelta(expireUnit, expireValue)
        )

    def archiveInteractionDetails(self, expireUnit, expireValue):
        self.checkDatabases(
            self.db.stmUserInteractionDetails,
            lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
            self.moveInteractionDetails,
            self.getTimedelta(expireUnit, expireValue)
        )

    def archiveImageDetails(self, expireUnit, expireValue):
        self.checkDatabases(
            self.db.stmCreatedImageDetails,
            lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
            self.moveImageDetails,
            self.getTimedelta(expireUnit, expireValue)
        )

    def archiveCreatedImages(self, expireUnit, expireValue):
        expireDelta = self.getTimedelta(expireUnit, expireValue)

        for root, _, files in os.walk(self.db.createdImages, topdown=False):
            for file in files:
                try:
                    if not file.lower().endswith(".png"):
                        continue

                    filePath = self.getDir(root, file)
                    fileTime = datetime.fromtimestamp(os.path.getmtime(filePath))

                    if datetime.now() - fileTime > expireDelta:
                        relativePath = os.path.relpath(filePath, self.db.createdImages)
                        destPath = self.getDir(self.db.ltmCreatedImages, relativePath)

                        os.makedirs(os.path.dirname(destPath), exist_ok=True)
                        shutil.move(filePath, destPath)

                except Exception as e:
                    logger.error(f"MemoryMaintenance Error archiving image '{file}':", exc_info=True)


    # ========== Move Helpers ==========

    def moveConversationDetails(self, dbFile, fileName):
        if not os.path.exists(dbFile):
            return

        userName = os.path.splitext(fileName)[0]
        ltmPath  = self.getDir(self.db.ltmUserConversationDetails, "LTM.db")

        selectQuery = f'''
            SELECT '{userName}' AS user, dtStamp, content, response FROM memory
        '''

        try:
            with self.dbLock, sqlite3.connect(dbFile) as srcConn:
                srcCursor = srcConn.cursor()

                # Verify memory table exists
                srcCursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory'")
                if not srcCursor.fetchone():
                    return

                srcCursor.execute(selectQuery)
                rows = srcCursor.fetchall()
                if not rows:
                    return  # 🔥 skip if no rows

        except Exception as e:
            logger.error(f"Error pre-checking '{dbFile}':", exc_info=True)
            return

        self.createMemoryDatabase(ltmPath)  # only reaches here if data exists

        self.moveDatabase(
            srcFile  = dbFile,
            destFile = ltmPath,
            createQuery='''
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT,
                    dtStamp TEXT,
                    content TEXT,
                    response TEXT
                )
            ''',
            selectQuery=selectQuery,
            insertQuery='''
                INSERT INTO memory (user, dtStamp, content, response)
                VALUES (?, ?, ?, ?)
            '''
        )

    def moveInteractionDetails(self, dbFile, fileName):
        self.createDetailsDatabase(dbFile)
        ltmPath = self.getDir(self.db.ltmUserInteractionDetails, fileName)
        self.moveDatabase(
            dbFile,
            ltmPath,
            '''CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY AUTOINCREMENT, dtStamp TEXT, content TEXT)''',
            'SELECT dtStamp, content FROM memory',
            'INSERT INTO memory (dtStamp, content) VALUES (?, ?)'
        )

    def moveImageDetails(self, dbFile, fileName):
        self.createDetailsDatabase(dbFile)
        ltmPath = self.getDir(self.db.ltmCreatedImageDetails, fileName)
        self.moveDatabase(
            dbFile,
            ltmPath,
            '''CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY AUTOINCREMENT, dtStamp TEXT, content TEXT)''',
            'SELECT dtStamp, content FROM memory',
            'INSERT INTO memory (dtStamp, content) VALUES (?, ?)'
        )
