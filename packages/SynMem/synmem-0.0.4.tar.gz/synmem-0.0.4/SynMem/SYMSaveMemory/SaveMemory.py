
import os
from pathlib import Path
import sqlite3
import threading
from datetime import datetime, timedelta
from functools import partial
import shutil
import time
import base64
from PIL import Image
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


class SaveMemory:
    def __init__(self, dbLock):
        self.dbLock = dbLock

    def createInteractionDatabase(self, user, path):
        self.createPersonalDatabase(self.getDir(path, f"{user}.db"))

    def createDatabase(self, dbPath, tableSchema):
        if not os.path.exists(dbPath):
            with self.dbLock, sqlite3.connect(dbPath) as conn:
                cursor = conn.cursor()
                cursor.execute(tableSchema)
                conn.commit()

    def createPersonalDatabase(self, dbPath):
        tableSchema = '''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dtStamp TEXT,
                content TEXT,
                response TEXT
            )
        '''
        self.createDatabase(dbPath, tableSchema)

    def createMemoryDatabase(self, dbPath):
        tableSchema = '''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT,
                dtStamp TEXT,
                content TEXT,
                response TEXT
            )
        '''
        self.createDatabase(dbPath, tableSchema)

    def createDetailsDatabase(self, dbPath):
        tableSchema = '''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dtStamp TEXT,
                content TEXT
            )
        '''
        self.createDatabase(dbPath, tableSchema)

    def saveData(self, dbDir, ctx, response=None):
        # Convert content to a text string.
        timestamp = datetime.now().isoformat()
        contentText = (
            ctx.decode('utf-8', errors='replace') if isinstance(ctx, bytes)
            else ctx if isinstance(ctx, str)
            else str(ctx)
        )

        try:
            with self.dbLock, sqlite3.connect(dbDir) as conn:
                cursor = conn.cursor()
                # Check what columns exist in the memory table.
                cursor.execute("PRAGMA table_info(memory)")
                columns = [column[1] for column in cursor.fetchall()]

                if 'response' in columns:
                    cursor.execute(
                        'INSERT INTO memory (dtStamp, content, response) VALUES (?, ?, ?)',
                        (timestamp, contentText, response)
                    )
                else:
                    cursor.execute(
                        'INSERT INTO memory (dtStamp, content) VALUES (?, ?)',
                        (timestamp, contentText)
                    )
                conn.commit()
            return
        except sqlite3.OperationalError as e:
            logger.error(f"OperationalError while saving data:", exc_info=True)
        except Exception as e:
            logger.error(f"Unexpected error while saving data:", exc_info=True)

    def saveSensory(self, ctx, response, user, path, limit):
        self.createPersonalDatabase(self.getDir(path, f"{user()}.db"))
        db = self.getDir(path, f"{user()}.db")

        with self.dbLock, sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM memory')
            count = cursor.fetchone()[0]

            if count  >= limit:
                cursor.execute('DELETE FROM memory WHERE id = (SELECT MIN(id) FROM memory)')
                conn.commit()

        self.saveData(db, ctx, response)

    def saveConversationDetails(self, ctx, response, user, path):
        dbPath      = self.getDir(path, "STM.db")
        userName    = user()
        timestamp   = datetime.now().isoformat()
        contentText = (
            ctx.decode('utf-8', errors='replace') if isinstance(ctx, bytes)
            else ctx if isinstance(ctx, str)
            else str(ctx)
        )


        self.createMemoryDatabase(dbPath)

        try:
            with self.dbLock, sqlite3.connect(dbPath) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO memory (user, dtStamp, content, response) VALUES (?, ?, ?, ?)",
                    (userName, timestamp, contentText, response)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving data to {dbPath}:", exc_info=True)

    def saveInteractionDetails(self, user, path):
        db = self.getDir(path, "Details.db")
        self.createDetailsDatabase(db)
        self.saveData(db, user())

    def saveImageDetails(self, imageSubject, path):
        db = self.getDir(path, "Details.db")
        self.createDetailsDatabase(db)
        self.saveData(db, imageSubject)

    def getDir(self, *paths):
        return str(Path(*paths).resolve())

    def setImageDir(self, base):
        now    = datetime.now()
        return self.getDir(base, now.strftime("%Y").lower(), now.strftime("%m"), now.strftime("%d").lower())

    def getNextAvailableFilename(self, directory, baseName, extension=".png"):
        counter = 1
        while True:
            filename = f"{baseName}{counter}{extension}"
            filePath = self.getDir(directory, filename)
            if not os.path.exists(filePath):
                return filename
            counter += 1

    def saveCreatedImage(self, imageSubject, imageData, path):
        image    = Image.open(BytesIO(imageData.content))
        imageDir = self.setImageDir(path)
        os.makedirs(imageDir, exist_ok=True)
        filename  = self.getNextAvailableFilename(imageDir, imageSubject, ".png")
        imagePath = self.getDir(imageDir, filename)

        self.saveImageDetails(filename)
        image.save(imagePath)
        image.show()
