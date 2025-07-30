
import os
from pathlib import Path
import sqlite3
import threading
from datetime import datetime, timedelta
import shutil
import time
from PIL import Image
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class SynMem:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(SynMem, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self.dbLock = threading.Lock()
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.sessionStart = datetime.now()

        self.sensoryLimit       = 10
        self.sensoryExpireUnit  = "days"
        self.sensoryExpireValue = 7

        self.memoryExpireUnit   = "minutes"
        self.memoryExpireValue  = 30

        self.imageExpireUnit    = "days"
        self.imageExpireValue   = 30

        self.cleanupExpireUnit  = "days"
        self.cleanupExpireValue = 15

        self.perceptionLimit    = 10
        self.perception         = []

        self.senDir = None

        self.stmUserConversationDetails = None
        self.stmUserInteractionDetails  = None

        self.ltmUserConversationDetails = None
        self.ltmUserInteractionDetails  = None

        self.stmCreatedImages = None
        self.ltmCreatedImages = None

        self.stmCreatedImageDetails = None
        self.ltmCreatedImageDetails = None

    def setSynMemDirs(self, dirs):
        attrNames = [
            'senDir',
            'stmUserConversationDetails', 'stmUserInteractionDetails',
            'ltmUserConversationDetails', 'ltmUserInteractionDetails',
            'stmCreatedImages', 'ltmCreatedImages',
            'stmCreatedImageDetails', 'ltmCreatedImageDetails'
        ]
        if isinstance(dirs, dict):
            for attr in attrNames:
                setattr(self, attr, dirs.get(attr))
        else:
            for attr, value in zip(attrNames, dirs + [None] * (len(attrNames) - len(dirs))):
                setattr(self, attr, value)

    def setSynMemConfig(self, config):
        attrDefaults = [
            ('perceptionLimit',    10),
            ('sensoryLimit',       10),
            ('sensoryExpireUnit',  "days"),
            ('sensoryExpireValue', 7),
            ('memoryExpireUnit',   "minutes"),
            ('memoryExpireValue',  30),
            ('imageExpireUnit',    "days"),
            ('imageExpireValue',   30),
            ('cleanupExpireUnit',  "days"),
            ('cleanupExpireValue', 15),
        ]
        if isinstance(config, dict):
            for attr, default in attrDefaults:
                setattr(self, attr, config.get(attr, default))
        else:
            for idx, (attr, default) in enumerate(attrDefaults):
                setattr(self, attr, config[idx] if idx < len(config) else default)

    def getTimedelta(self, unit, value):
        return timedelta(**{unit: value})

    def getDir(self, *paths):
        return str(Path(*paths).resolve())

    def ensureDir(self, path):
        dirName = os.path.dirname(path)
        if dirName and not os.path.exists(dirName):
            os.makedirs(dirName, exist_ok=True)

    # Database creation
    def createDatabase(self, path, tableSchema):
        self.ensureDir(path)
        if not os.path.exists(path):
            with self.dbLock, sqlite3.connect(path) as conn:
                cursor = conn.cursor()
                cursor.execute(tableSchema)
                conn.commit()

    def createPersonalDatabase(self, path):
        tableSchema = '''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dtStamp TEXT,
                content TEXT,
                response TEXT
            )
        '''
        self.createDatabase(path, tableSchema)

    def createMemoryDatabase(self, path):
        tableSchema = '''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT,
                dtStamp TEXT,
                content TEXT,
                response TEXT
            )
        '''
        self.createDatabase(path, tableSchema)

    def createDetailsDatabase(self, path):
        tableSchema = '''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dtStamp TEXT,
                content TEXT
            )
        '''
        self.createDatabase(path, tableSchema)

    # Save
    def savePerception(self, ctx: str):
        if len(self.perception) >= self.perceptionLimit:
            self.perception.pop(0)
        self.perception.append(ctx)

    def saveData(self, path, ctx, response=None):
        self.ensureDir(path)
        timestamp = datetime.now().isoformat()
        contentText = (
            ctx.decode('utf-8', errors='replace') if isinstance(ctx, bytes)
            else ctx if isinstance(ctx, str)
            else str(ctx)
        )
        try:
            with self.dbLock, sqlite3.connect(path) as conn:
                cursor = conn.cursor()
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
        except sqlite3.OperationalError:
            logger.error(f"OperationalError while saving data:", exc_info=True)
        except Exception:
            logger.error(f"Unexpected error while saving data:", exc_info=True)

    def saveSensory(self, ctx, response, user, path):
        self.ensureDir(path)
        self.createPersonalDatabase(self.getDir(path, f"{user}.db"))
        db = self.getDir(path, f"{user}.db")
        self.ensureDir(db)
        with self.dbLock, sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM memory')
            count = cursor.fetchone()[0]
            if count >= self.sensoryLimit:
                cursor.execute('DELETE FROM memory WHERE id = (SELECT MIN(id) FROM memory)')
                conn.commit()
        self.saveData(db, ctx, response)

    def saveConversationDetails(self, ctx, response, user, path):
        db = self.getDir(path, "STM.db")
        self.ensureDir(db)
        timestamp = datetime.now().isoformat()
        contentText = (
            ctx.decode('utf-8', errors='replace') if isinstance(ctx, bytes)
            else ctx if isinstance(ctx, str)
            else str(ctx)
        )
        self.createMemoryDatabase(db)
        try:
            with self.dbLock, sqlite3.connect(db) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO memory (user, dtStamp, content, response) VALUES (?, ?, ?, ?)",
                    (user, timestamp, contentText, response)
                )
                conn.commit()
        except Exception:
            logger.error(f"Error saving data to {db}:", exc_info=True)

    def saveInteractionDetails(self, user, path):
        db = self.getDir(path, "Details.db")
        self.ensureDir(db)
        self.createDetailsDatabase(db)
        self.saveData(db, user)

    def saveImageDetails(self, imageSubject, path):
        db = self.getDir(path, "Details.db")
        self.ensureDir(db)
        self.createDetailsDatabase(db)
        self.saveData(db, imageSubject)

    def setImageDir(self, base):
        now = datetime.now()
        return self.getDir(base, now.strftime("%Y").lower(), now.strftime("%m"), now.strftime("%d").lower())

    def getNextAvailableFilename(self, directory, baseName, extension=".png"):
        counter = 1
        while True:
            filename = f"{baseName}{counter}{extension}"
            filePath = self.getDir(directory, filename)
            if not os.path.exists(filePath):
                return filename
            counter += 1

    def saveCreatedImage(self, imageSubject, imageData, path1, path2):
        image = Image.open(BytesIO(imageData.content))
        imageDir = self.setImageDir(path1)
        self.ensureDir(imageDir)
        filename = self.getNextAvailableFilename(imageDir, imageSubject, ".png")
        imagePath = self.getDir(imageDir, filename)
        self.ensureDir(imagePath)
        self.saveImageDetails(filename, path2)
        image.save(imagePath)
        image.show()

    # Retrieve
    def retrievePerception(self):
        if self.perception:
            return "\n".join(self.perception)
        else:
            return "No Perception Feedback Available."

    def retrieveMemoryFromDb(self, dbFile, query, params, returnTimestampOnly=False):
        memory = []
        if os.path.exists(dbFile):
            try:
                with self.dbLock, sqlite3.connect(dbFile) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
                    if rows:
                        for row in rows:
                            if isinstance(row, tuple) and len(row) > 0:
                                if returnTimestampOnly:
                                    memory.append(row[0])
                                else:
                                    timestamp = row[0]
                                    rawContent = row[1]
                                    response = row[2] if len(row) > 2 else ""
                                    decodedContent = rawContent if isinstance(rawContent, str) else str(rawContent)
                                    memory.append((timestamp, decodedContent, response))
                            else:
                                logger.warning(f"Skipping invalid row format in {dbFile}: {row}")
                    return memory
            except sqlite3.OperationalError:
                logger.error(f"OperationalError while retrieving data from {dbFile}:", exc_info=True)
            except Exception:
                logger.error(f"Unexpected error while retrieving data from {dbFile}:", exc_info=True)
        return memory

    def retrieveDetailsFromDb(self, dbFile, query, params):
        memory = []
        if os.path.exists(dbFile):
            with self.dbLock, sqlite3.connect(dbFile) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                for row in rows:
                    timestamp = row[0]
                    contentText = row[1] if isinstance(row[1], str) else str(row[1])
                    memory.append((timestamp, contentText))
        return memory

    def retrieveSensory(self, path):
        query  = 'SELECT dtStamp, content, response FROM memory'
        params = []
        return self.retrieveMemoryFromDb(path, query, params)

    def retrieveConversationDetails(self, user, paths: list, startDate=None, endDate=None):
        dbNames = ["STM.db", "LTM.db"]
        dbs = [self.getDir(path, dbName) for path, dbName in zip(paths, dbNames)]
        query = 'SELECT dtStamp, content, response FROM memory WHERE user = ? COLLATE NOCASE'
        params = [user]
        if startDate:
            startDate = self.formatIsoDate(startDate)
            query += ' AND dtStamp >= ?'
            params.append(startDate)
        if endDate:
            endDate = self.formatIsoDate(endDate)
            query += ' AND dtStamp <= ?'
            params.append(endDate)
        memory = []
        for db in dbs:
            memory += self.retrieveMemoryFromDb(db, query, params)
        return memory

    def retrieveInteractionDetails(self, paths: list, startDate=None, endDate=None):
        dbs = [self.getDir(path, "Details.db") for path in paths]
        query = 'SELECT dtStamp, content FROM memory WHERE 1=1'
        params = []
        if startDate:
            startDate = self.formatIsoDate(startDate)
            query += ' AND dtStamp >= ?'
            params.append(startDate)
        if endDate:
            endDate = self.formatIsoDate(endDate)
            query += ' AND dtStamp <= ?'
            params.append(endDate)
        memory = []
        for db in dbs:
            memory += self.retrieveDetailsFromDb(db, query, params)
        return memory

    def retrieveLastInteractionTime(self, user, paths: list):
        dbConfigs = [
            (f"{user}.db", 'SELECT dtStamp FROM memory ORDER BY dtStamp DESC LIMIT 1', []),
            ("STM.db", 'SELECT dtStamp FROM memory WHERE user = ? COLLATE NOCASE ORDER BY dtStamp DESC LIMIT 1', [user]),
            ("LTM.db", 'SELECT dtStamp FROM memory WHERE user = ? COLLATE NOCASE ORDER BY dtStamp DESC LIMIT 1', [user])
        ]
        for i, path in enumerate(paths[:len(dbConfigs)]):
            dbName, query, params = dbConfigs[i]
            dbPath = self.getDir(path, dbName)
            timestamps = self.retrieveMemoryFromDb(dbPath, query, params, returnTimestampOnly=True)
            if timestamps:
                try:
                    return datetime.now() - datetime.fromisoformat(timestamps[0])
                except ValueError:
                    logger.warning(f"Invalid timestamp in DB: {timestamps[0]}")
        return datetime.now() - self.sessionStart

    def retrieveLastInteractionDate(self, user, paths: list):
        dbConfigs = [
            (f"{user}.db", 'SELECT dtStamp FROM memory ORDER BY dtStamp DESC LIMIT 1', []),
            ("STM.db", 'SELECT dtStamp FROM memory WHERE user = ? COLLATE NOCASE ORDER BY dtStamp DESC LIMIT 1', [user]),
            ("LTM.db", 'SELECT dtStamp FROM memory WHERE user = ? COLLATE NOCASE ORDER BY dtStamp DESC LIMIT 1', [user])
        ]
        for i, path in enumerate(paths[:len(dbConfigs)]):
            dbName, query, params = dbConfigs[i]
            dbPath = self.getDir(path, dbName)
            timestamps = self.retrieveMemoryFromDb(dbPath, query, params, returnTimestampOnly=True)
            if timestamps:
                try:
                    return datetime.fromisoformat(timestamps[0])
                except ValueError:
                    logger.warning(f"Invalid timestamp in DB: {timestamps[0]}")
        return self.sessionStart

    def retrieveImageDetails(self, paths: list, startDate=None, endDate=None):
        dbs = [self.getDir(path, "Details.db") for path in paths]
        query = 'SELECT dtStamp, content FROM memory WHERE 1=1'
        params = []
        if startDate:
            startDate = self.formatIsoDate(startDate)
            query += ' AND dtStamp >= ?'
            params.append(startDate)
        if endDate:
            endDate = self.formatIsoDate(endDate)
            query += ' AND dtStamp <= ?'
            params.append(endDate)
        memory = []
        for db in dbs:
            memory += self.retrieveDetailsFromDb(db, query, params)
        return memory

    def retrieveCreatedImage(self, directory, imageName):
        imagePath = self.getImageDir(directory, f"{imageName}.png")
        if os.path.exists(imagePath):
            with Image.open(imagePath) as img:
                img.show()
            return imagePath
        else:
            logger.warning(f"Image not found: {imagePath}")
            return f"Image not found: {imagePath}"

    def getImageDir(self, base, date):
        return self.getDir(base, date.strftime("%Y").lower(), date.strftime("%m"), date.strftime("%d").lower())

    def formatIsoDate(self, dateStr):
        if not dateStr:
            return None
        inputFormats = [
            "%m-%d-%Y", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y",
            "%m-%d-%y", "%d-%m-%y", "%m/%d/%y", "%d/%m/%y",
            "%m-%d-%Y %I:%M %p", "%d-%m-%Y %I:%M %p",
            "%m/%d/%Y %I:%M %p", "%d/%m/%Y %I:%M %p",
            "%Y-%m-%d %I:%M %p",
            "%I:%M %p",
            "%H:%M"
        ]
        today = datetime.today()
        try:
            dt = datetime.fromisoformat(dateStr)
        except ValueError:
            dt = self._parseKnownFormats(dateStr, inputFormats, today)
        isoDate = dt.isoformat(timespec="seconds")
        return isoDate if "T" in dateStr else f"{isoDate.split('T')[0]}T00:00:00"

    def _parseKnownFormats(self, dateStr, formats, today):
        for fmt in formats:
            try:
                dt = datetime.strptime(dateStr, fmt)
                if fmt in ("%I:%M %p", "%H:%M"):
                    dt = today.replace(hour=dt.hour, minute=dt.minute, second=0, microsecond=0)
                return dt
            except ValueError:
                continue
        raise ValueError(
            f"Invalid date format: {dateStr}. Expected ISO format YYYY-MM-DD or formats like MM-DD-YYYY, DD-MM-YYYY, MM/DD/YYYY, DD/MM/YYYY, or even just time (e.g., 6:30 PM)."
        )

    # Clear (all user queries use COLLATE NOCASE)
    def clearPerception(self):
        self.perception.clear()
        print("Perception Feedback Cleared.")

    def clearFirstEntry(self):
        self._clearEntryByQuery('MIN')

    def clearLastEntry(self):
        self._clearEntryByQuery('MAX')

    def clearAllEntries(self):
        user  = self.getCurrentUserName()
        senDb = self.getDir(self.senDir,                     f"{user}.db")
        stmDb = self.getDir(self.stmUserConversationDetails, "STM.db")
        ltmDb = self.getDir(self.ltmUserConversationDetails, "LTM.db")
        self._deleteByQuery(senDb, "DELETE FROM memory")
        self._deleteByQuery(stmDb, "DELETE FROM memory WHERE user = ? COLLATE NOCASE", [user])
        self._deleteByQuery(ltmDb, "DELETE FROM memory WHERE user = ? COLLATE NOCASE", [user])

    def _clearEntryByQuery(self, which):
        user  = self.getCurrentUserName()
        senDb = self.getDir(self.senDir,                     f"{user}.db")
        stmDb = self.getDir(self.stmUserConversationDetails, "STM.db")
        ltmDb = self.getDir(self.ltmUserConversationDetails, "LTM.db")
        # SEN (no user column)
        self._deleteByQuery(
            senDb,
            f"DELETE FROM memory WHERE id = (SELECT {which}(id) FROM memory)"
        )
        # STM + LTM (case-insensitive)
        self._deleteByQuery(
            stmDb,
            f"DELETE FROM memory WHERE id = (SELECT {which}(id) FROM memory WHERE user = ? COLLATE NOCASE) AND user = ? COLLATE NOCASE",
            [user, user]
        )
        self._deleteByQuery(
            ltmDb,
            f"DELETE FROM memory WHERE id = (SELECT {which}(id) FROM memory WHERE user = ? COLLATE NOCASE) AND user = ? COLLATE NOCASE",
            [user, user]
        )

    def _deleteByQuery(self, path, query, params=None):
        if os.path.exists(path):
            try:
                with self.dbLock, sqlite3.connect(path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params or [])
                    conn.commit()
            except Exception:
                logger.error(f"Failed to clear from {path}:", exc_info=True)

    # View
    def viewDatabase(self, path, limit=None):
        return self._viewTable(path, "memory", limit)

    def viewDetailsDatabase(self, path, limit=None):
        return self._viewTable(path, "memory", limit)

    def _viewTable(self, path, tableName, limit=None):
        if not os.path.exists(path):
            logger.warning(f"Database not found: {path}")
            return []
        try:
            with self.dbLock, sqlite3.connect(path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tableName}'")
                if not cursor.fetchone():
                    logger.warning(f"No '{tableName}' table in: {path}")
                    return []
                cursor.execute(f"PRAGMA table_info({tableName})")
                columns = [col[1] for col in cursor.fetchall()]
                query = f"SELECT * FROM {tableName}"
                if limit:
                    query += f" ORDER BY id DESC LIMIT {limit}"
                cursor.execute(query)
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        except Exception:
            logger.error(f"[Viewer] Error reading {path}:", exc_info=True)
            return []











# import os
# from pathlib import Path
# import sqlite3
# import threading
# from datetime import datetime, timedelta
# import shutil
# import time
# from PIL import Image
# from io import BytesIO
# import logging


# # from .SYMViewMemory.ViewMemory import ViewMemory
# # from .SYMMemoryMaintenance.MemoryMaintenance import MemoryMaintenance
# # from .SYMClearMemory.ClearMemory import ClearMemory
# # from .SYMSaveMemory.SaveMemory import SaveMemory
# # from .SYMRetrieveMemory.RetrieveMemory import RetrieveMemory

# logger = logging.getLogger(__name__)

# class SynMem:
#     _instance = None
#     _lock = threading.Lock()

#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             with cls._lock:
#                 if not cls._instance:
#                     cls._instance = super(SynMem, cls).__new__(cls)
#         return cls._instance

#     def __init__(self):
#         if hasattr(self, 'initialized'):
#             return
#         self.dbLock = threading.Lock()
#         self._initComponents()
#         self.initialized = True 

#     def _initComponents(self):
#         self.sessionStart = datetime.now()

#         self.sensoryLimit       = 10
#         self.sensoryExpireUnit  = "days"
#         self.sensoryExpireValue = 7

#         self.memoryExpireUnit   = "minutes"
#         self.memoryExpireValue  = 30

#         self.imageExpireUnit    = "days"
#         self.imageExpireValue   = 30

#         self.cleanupExpireUnit  = "days"
#         self.cleanupExpireValue = 15

#         self.perceptionLimit    = 10
#         self.perception         = []

#         self.senDir = None

#         self.stmUserConversationDetails = None
#         self.stmUserInteractionDetails  = None

#         self.ltmUserConversationDetails = None
#         self.ltmUserInteractionDetails  = None

#         self.stmCreatedImages = None
#         self.ltmCreatedImages = None

#         self.stmCreatedImageDetails = None
#         self.ltmCreatedImageDetails = None
        
#     # def setSynMemDirs(self, dirs: list):
#     #     attrNames = [
#     #         'senDir',
#     #         'stmUserConversationDetails', 'stmUserInteractionDetails',
#     #         'ltmUserConversationDetails', 'ltmUserInteractionDetails',
#     #         'stmCreatedImages', 'ltmCreatedImages',
#     #         'stmCreatedImageDetails', 'ltmCreatedImageDetails'
#     #     ]
#     #     # Map provided dirs to attributes, fill missing with None
#     #     for attr, value in zip(attrNames, dirs + [None] * (len(attrNames) - len(dirs))):
#     #         setattr(self, attr, value)

#     # def setSynMemConfig(self, config: list):
#     #     attrDefaults = [
#     #         ('sensoryLimit',       10),
#     #         ('sensoryExpireUnit',  "days"),
#     #         ('sensoryExpireValue', 7),
#     #         ('memoryExpireUnit',   "minutes"),
#     #         ('memoryExpireValue',  30),
#     #         ('imageExpireUnit',    "days"),
#     #         ('imageExpireValue',   30),
#     #         ('cleanupExpireUnit',  "days"),
#     #         ('cleanupExpireValue', 15),
#     #         ('perceptionLimit',    10),
#     #     ]
#     #     for idx, (attr, default) in enumerate(attrDefaults):
#     #         # Use provided config if available, otherwise fall back to default
#     #         setattr(self, attr, config[idx] if idx < len(config) else default)
#     def setSynMemDirs(self, dirs):
#         attrNames = [
#             'senDir',
#             'stmUserConversationDetails', 'stmUserInteractionDetails',
#             'ltmUserConversationDetails', 'ltmUserInteractionDetails',
#             'stmCreatedImages', 'ltmCreatedImages',
#             'stmCreatedImageDetails', 'ltmCreatedImageDetails'
#         ]
#         if isinstance(dirs, dict):
#             for attr in attrNames:
#                 setattr(self, attr, dirs.get(attr))
#         else:
#             for attr, value in zip(attrNames, dirs + [None] * (len(attrNames) - len(dirs))):
#                 setattr(self, attr, value)


#     def setSynMemConfig(self, config):
#         attrDefaults = [
#             ('perceptionLimit',    10),
#             ('sensoryLimit',       10),
#             ('sensoryExpireUnit',  "days"),
#             ('sensoryExpireValue', 7),
#             ('memoryExpireUnit',   "minutes"),
#             ('memoryExpireValue',  30),
#             ('imageExpireUnit',    "days"),
#             ('imageExpireValue',   30),
#             ('cleanupExpireUnit',  "days"),
#             ('cleanupExpireValue', 15),
#         ]
#         if isinstance(config, dict):
#             for attr, default in attrDefaults:
#                 setattr(self, attr, config.get(attr, default))
#         else:
#             for idx, (attr, default) in enumerate(attrDefaults):
#                 setattr(self, attr, config[idx] if idx < len(config) else default)



   
#     def getTimedelta(self, unit, value):
#         return timedelta(**{unit: value})

#     def getDir(self, *paths):
#         return str(Path(*paths).resolve())

#     def ensureDir(self, path):
#         dirName = os.path.dirname(path)
#         if dirName and not os.path.exists(dirName):
#             os.makedirs(dirName, exist_ok=True)


#     # ─── Database ────────────────────────────────────────────────────────
#     def createDatabase(self, path, tableSchema):
#         self.ensureDir(path)
#         if not os.path.exists(path):
#             with self.dbLock, sqlite3.connect(path) as conn:
#                 cursor = conn.cursor()
#                 cursor.execute(tableSchema)
#                 conn.commit()

#     def createPersonalDatabase(self, path):
#         tableSchema = '''
#             CREATE TABLE IF NOT EXISTS memory (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 dtStamp TEXT,
#                 content TEXT,
#                 response TEXT
#             )
#         '''
#         self.createDatabase(path, tableSchema)

#     def createMemoryDatabase(self, path):
#         tableSchema = '''
#             CREATE TABLE IF NOT EXISTS memory (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user TEXT,
#                 dtStamp TEXT,
#                 content TEXT,
#                 response TEXT
#             )
#         '''
#         self.createDatabase(path, tableSchema)

#     def createDetailsDatabase(self, path):
#         tableSchema = '''
#             CREATE TABLE IF NOT EXISTS memory (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 dtStamp TEXT,
#                 content TEXT
#             )
#         '''
#         self.createDatabase(path, tableSchema)

#     # ─── Save ────────────────────────────────────────────────────────
#     def savePerception(self, ctx: str):
#         if len(self.perception) >= self.perceptionLimit:
#             self.perception.pop(0)
#         self.perception.append(ctx)

#     def saveData(self, path, ctx, response=None):
#         self.ensureDir(path)
#         # Convert content to a text string.
#         timestamp = datetime.now().isoformat()
#         contentText = (
#             ctx.decode('utf-8', errors='replace') if isinstance(ctx, bytes)
#             else ctx if isinstance(ctx, str)
#             else str(ctx)
#         )

#         try:
#             with self.dbLock, sqlite3.connect(path) as conn:
#                 cursor = conn.cursor()
#                 # Check what columns exist in the memory table.
#                 cursor.execute("PRAGMA table_info(memory)")
#                 columns = [column[1] for column in cursor.fetchall()]

#                 if 'response' in columns:
#                     cursor.execute(
#                         'INSERT INTO memory (dtStamp, content, response) VALUES (?, ?, ?)',
#                         (timestamp, contentText, response)
#                     )
#                 else:
#                     cursor.execute(
#                         'INSERT INTO memory (dtStamp, content) VALUES (?, ?)',
#                         (timestamp, contentText)
#                     )
#                 conn.commit()
#             return
#         except sqlite3.OperationalError as e:
#             logger.error(f"OperationalError while saving data:", exc_info=True)
#         except Exception as e:
#             logger.error(f"Unexpected error while saving data:", exc_info=True)

#     def saveSensory(self, ctx, response, user, path):
#         self.ensureDir(path)
#         self.createPersonalDatabase(self.getDir(path, f"{user}.db"))
#         db = self.getDir(path, f"{user}.db")
#         self.ensureDir(db)
#         with self.dbLock, sqlite3.connect(db) as conn:
#             cursor = conn.cursor()
#             cursor.execute('SELECT COUNT(*) FROM memory')
#             count = cursor.fetchone()[0]

#             if count  >= self.sensoryLimit:
#                 cursor.execute('DELETE FROM memory WHERE id = (SELECT MIN(id) FROM memory)')
#                 conn.commit()

#         self.saveData(db, ctx, response)

#     def saveConversationDetails(self, ctx, response, user, path):
#         db        = self.getDir(path, "STM.db")
#         self.ensureDir(db)
#         timestamp   = datetime.now().isoformat()
#         contentText = (
#             ctx.decode('utf-8', errors='replace') if isinstance(ctx, bytes)
#             else ctx if isinstance(ctx, str)
#             else str(ctx)
#         )


#         self.createMemoryDatabase(db)

#         try:
#             with self.dbLock, sqlite3.connect(db) as conn:
#                 cursor = conn.cursor()
#                 cursor.execute(
#                     "INSERT INTO memory (user, dtStamp, content, response) VALUES (?, ?, ?, ?)",
#                     (user, timestamp, contentText, response)
#                 )
#                 conn.commit()
#         except Exception as e:
#             logger.error(f"Error saving data to {db}:", exc_info=True)

#     def saveInteractionDetails(self, user, path):
#         db = self.getDir(path, "Details.db")
#         self.ensureDir(db)
#         self.createDetailsDatabase(db)
#         self.saveData(db, user)

#     def saveImageDetails(self, imageSubject, path):
#         db = self.getDir(path, "Details.db")
#         self.ensureDir(db)
#         self.createDetailsDatabase(db)
#         self.saveData(db, imageSubject)

#     def setImageDir(self, base):
#         now    = datetime.now()
#         return self.getDir(base, now.strftime("%Y").lower(), now.strftime("%m"), now.strftime("%d").lower())

#     def getNextAvailableFilename(self, directory, baseName, extension=".png"):
#         counter = 1
#         while True:
#             filename = f"{baseName}{counter}{extension}"
#             filePath = self.getDir(directory, filename)
#             if not os.path.exists(filePath):
#                 return filename
#             counter += 1

#     def saveCreatedImage(self, imageSubject, imageData, path1, path2):
#         image    = Image.open(BytesIO(imageData.content))
#         imageDir = self.setImageDir(path1)
#         self.ensureDir(imageDir)

#         filename  = self.getNextAvailableFilename(imageDir, imageSubject, ".png")
#         imagePath = self.getDir(imageDir, filename)
#         self.ensureDir(imagePath)
#         self.saveImageDetails(filename, path2)
#         image.save(imagePath)
#         image.show()

#     # ─── Retrieve ────────────────────────────────────────────────────────
#     def retrievePerception(self):
#         if self.perception:
#             # Get everything in the perception list
#             perception = "\n".join(self.perception)
#             return perception
#         else:
#             #pass
#             return "No Perception Feedback Available."

#     def retrieveMemoryFromDb(self, dbFile, query, params, returnTimestampOnly=False):
#         memory = []
#         if os.path.exists(dbFile):
#             try:
#                 with self.dbLock, sqlite3.connect(dbFile) as conn:
#                     cursor = conn.cursor()
#                     cursor.execute(query, params)
#                     rows = cursor.fetchall()
#                     if rows:
#                         for row in rows:
#                             if isinstance(row, tuple) and len(row) > 0:
#                                 if returnTimestampOnly:
#                                     memory.append(row[0])
#                                 else:
#                                     timestamp = row[0]
#                                     rawContent = row[1]
#                                     response = row[2] if len(row) > 2 else ""
#                                     decodedContent = rawContent if isinstance(rawContent, str) else str(rawContent)
#                                     memory.append((timestamp, decodedContent, response))
#                             else:
#                                 logger.warning(f"Skipping invalid row format in {dbFile}: {row}")
#                     return memory
#             except sqlite3.OperationalError as e:
#                 logger.error(f"OperationalError while retrieving data from {dbFile}:", exc_info=True)
#             except Exception as e:
#                 logger.error(f"Unexpected error while retrieving data from {dbFile}:", exc_info=True)
#         return memory

#     def retrieveDetailsFromDb(self, dbFile, query, params):
#         memory = []
#         if os.path.exists(dbFile):
#             with self.dbLock, sqlite3.connect(dbFile) as conn:
#                 cursor = conn.cursor()
#                 cursor.execute(query, params)
#                 rows = cursor.fetchall()
#                 for row in rows:
#                     timestamp = row[0]
#                     contentText = row[1] if isinstance(row[1], str) else str(row[1])
#                     memory.append((timestamp, contentText))
#         return memory

#     def retrieveSensory(self, path):
#         query  = 'SELECT dtStamp, content, response FROM memory'
#         params = []
#         return self.retrieveMemoryFromDb(path, query, params)

#     def retrieveConversationDetails(self, user, paths: list, startDate=None, endDate=None):
#         dbNames = ["STM.db", "LTM.db"]
#         dbs = [self.getDir(path, dbName) for path, dbName in zip(paths, dbNames)]

#         query = 'SELECT dtStamp, content, response FROM memory WHERE user = ?'
#         params = [user]
#         if startDate:
#             startDate = self.formatIsoDate(startDate)
#             query += ' AND dtStamp >= ?'
#             params.append(startDate)
#         if endDate:
#             endDate = self.formatIsoDate(endDate)
#             query += ' AND dtStamp <= ?'
#             params.append(endDate)

#         memory = []
#         for db in dbs:
#             memory += self.retrieveMemoryFromDb(db, query, params)
#         return memory

#     def retrieveInteractionDetails(self, paths: list, startDate=None, endDate=None):
#         dbs = [self.getDir(path, "Details.db") for path in paths]

#         query = 'SELECT dtStamp, content FROM memory WHERE 1=1'
#         params = []
#         if startDate:
#             startDate = self.formatIsoDate(startDate)
#             query += ' AND dtStamp >= ?'
#             params.append(startDate)
#         if endDate:
#             endDate = self.formatIsoDate(endDate)
#             query += ' AND dtStamp <= ?'
#             params.append(endDate)

#         memory = []
#         for db in dbs:
#             memory += self.retrieveDetailsFromDb(db, query, params)
#         return memory

#     def retrieveLastInteractionTime(self, user, paths: list):
#         dbConfigs = [
#             (f"{user}.db", 'SELECT dtStamp FROM memory ORDER BY dtStamp DESC LIMIT 1', []),
#             ("STM.db", 'SELECT dtStamp FROM memory WHERE user = ? ORDER BY dtStamp DESC LIMIT 1', [user]),
#             ("LTM.db", 'SELECT dtStamp FROM memory WHERE user = ? ORDER BY dtStamp DESC LIMIT 1', [user])
#         ]
#         for i, path in enumerate(paths[:len(dbConfigs)]):
#             dbName, query, params = dbConfigs[i]
#             dbPath = self.getDir(path, dbName)
#             timestamps = self.retrieveMemoryFromDb(dbPath, query, params, returnTimestampOnly=True)
#             if timestamps:
#                 try:
#                     return datetime.now() - datetime.fromisoformat(timestamps[0])
#                 except ValueError:
#                     logger.warning(f"Invalid timestamp in DB: {timestamps[0]}")
#         return datetime.now() - self.sessionStart

#     def retrieveLastInteractionDate(self, user, paths: list):
#         dbConfigs = [
#             (f"{user}.db", 'SELECT dtStamp FROM memory ORDER BY dtStamp DESC LIMIT 1', []),
#             ("STM.db", 'SELECT dtStamp FROM memory WHERE user = ? ORDER BY dtStamp DESC LIMIT 1', [user]),
#             ("LTM.db", 'SELECT dtStamp FROM memory WHERE user = ? ORDER BY dtStamp DESC LIMIT 1', [user])
#         ]
#         for i, path in enumerate(paths[:len(dbConfigs)]):
#             dbName, query, params = dbConfigs[i]
#             dbPath = self.getDir(path, dbName)
#             timestamps = self.retrieveMemoryFromDb(dbPath, query, params, returnTimestampOnly=True)
#             if timestamps:
#                 try:
#                     return datetime.fromisoformat(timestamps[0])
#                 except ValueError:
#                     logger.warning(f"Invalid timestamp in DB: {timestamps[0]}")
#         return self.sessionStart

#     def retrieveImageDetails(self, paths: list, startDate=None, endDate=None):
#         dbs = [self.getDir(path, "Details.db") for path in paths]

#         query = 'SELECT dtStamp, content FROM memory WHERE 1=1'
#         params = []
#         if startDate:
#             startDate = self.formatIsoDate(startDate)
#             query += ' AND dtStamp >= ?'
#             params.append(startDate)
#         if endDate:
#             endDate = self.formatIsoDate(endDate)
#             query += ' AND dtStamp <= ?'
#             params.append(endDate)

#         memory = []
#         for db in dbs:
#             memory += self.retrieveDetailsFromDb(db, query, params)
#         return memory


#     def retrieveCreatedImage(self, directory, imageName):
#         imagePath = self.getImageDir(directory, f"{imageName}.png")
#         if os.path.exists(imagePath):
#             with Image.open(imagePath) as img:
#                 img.show()
#             return imagePath
#         else:
#             logger.warning(f"Image not found: {imagePath}")
#             return f"Image not found: {imagePath}"

#     def getImageDir(self, base, date):
#         return self.getDir(base, date.strftime("%Y").lower(), date.strftime("%m"), date.strftime("%d").lower())

#     def formatIsoDate(self, dateStr):
#         if not dateStr:
#             return None

#         inputFormats = [
#             "%m-%d-%Y", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y",
#             "%m-%d-%y", "%d-%m-%y", "%m/%d/%y", "%d/%m/%y",
#             "%m-%d-%Y %I:%M %p", "%d-%m-%Y %I:%M %p",
#             "%m/%d/%Y %I:%M %p", "%d/%m/%Y %I:%M %p",
#             "%Y-%m-%d %I:%M %p",
#             "%I:%M %p",
#             "%H:%M"
#         ]

#         today = datetime.today()

#         try:
#             dt = datetime.fromisoformat(dateStr)
#         except ValueError:
#             dt = self._parseKnownFormats(dateStr, inputFormats, today)

#         isoDate = dt.isoformat(timespec="seconds")
#         return isoDate if "T" in dateStr else f"{isoDate.split('T')[0]}T00:00:00"

#     def _parseKnownFormats(self, dateStr, formats, today):
#         for fmt in formats:
#             try:
#                 dt = datetime.strptime(dateStr, fmt)
#                 if fmt in ("%I:%M %p", "%H:%M"):
#                     dt = today.replace(hour=dt.hour, minute=dt.minute, second=0, microsecond=0)
#                 return dt
#             except ValueError:
#                 continue
#         raise ValueError(
#             f"Invalid date format: {dateStr}. Expected ISO format YYYY-MM-DD or formats like MM-DD-YYYY, DD-MM-YYYY, MM/DD/YYYY, DD/MM/YYYY, or even just time (e.g., 6:30 PM)."
#         )

#     # ─── Checks ────────────────────────────────────────────────────────
#     def startAutoMaintenance(self, interval=5*60):  # every 5 mins
#         def loop():
#             while True:
#                 self._performMaintenanceChecks()
#                 time.sleep(interval)
#         threading.Thread(target=loop, daemon=True).start()

#     def performStartupChecks(self, delay: int = 1):
#         checks = [
#             lambda: self.removeOldSensory(self.sensoryExpireUnit, self.sensoryExpireValue),
#             #lambda: self.archiveCreatedImages(self.imageExpireUnit, self.imageExpireValue),
#         ]
#         for check in checks:
#             check()
#             time.sleep(delay)

#     def _performMaintenanceChecks(self, delay: int = 1):
#         checks = [
#             lambda: self.archiveConversationDetails(self.memoryExpireUnit, self.memoryExpireValue),
#             lambda: self.archiveInteractionDetails(self.memoryExpireUnit, self.memoryExpireValue),
#             lambda: self.archiveImageDetails(self.memoryExpireUnit, self.memoryExpireValue),
#         ]
#         for check in checks:
#             check()
#             time.sleep(delay)

#     # ─── Maintenance ────────────────────────────────────────────────────────
#     def checkDatabases(self, sourceDir, timeCheckFunc, actionFunc, expireDelta):
#         if not sourceDir or not os.path.exists(sourceDir):
#             return
#         for root, _, files in os.walk(sourceDir, topdown=False):
#             for file in files:
#                 try:
#                     dbFile   = self.getDir(root, file)
#                     fileTime = timeCheckFunc(dbFile)
#                     if datetime.now() - fileTime > expireDelta:
#                         actionFunc(dbFile, file)
#                 except Exception as e:
#                     logger.error(f"Error processing {file}:", exc_info=True)

#     def moveDatabase(self, srcFile, destFile, createQuery, selectQuery, insertQuery):
#         os.makedirs(os.path.dirname(destFile), exist_ok=True)

#         # Ensure destination has table
#         with self.dbLock, sqlite3.connect(destFile) as destConn:
#             destCursor = destConn.cursor()
#             destCursor.execute(createQuery)
#             destConn.commit()

#         try:
#             with self.dbLock, sqlite3.connect(srcFile) as srcConn:
#                 srcCursor = srcConn.cursor()

#                 # Verify source table exists
#                 srcCursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory'")
#                 if not srcCursor.fetchone():
#                     logger.warning(f"Skipping '{srcFile}' - no memory table.")
#                     return

#                 srcCursor.execute(selectQuery)
#                 rows = srcCursor.fetchall()

#                 with sqlite3.connect(destFile) as destConn:
#                     destCursor = destConn.cursor()
#                     destCursor.executemany(insertQuery, rows)
#                     destConn.commit()

#                 srcCursor.execute("PRAGMA table_info(memory)")
#                 columns = [col[1] for col in srcCursor.fetchall()]
#                 hasUser = "user" in columns

#                 if hasUser:
#                     srcCursor.executemany(
#                         "DELETE FROM memory WHERE user = ? AND dtStamp = ?",
#                         [(row[0], row[1]) for row in rows]
#                     )
#                 else:
#                     srcCursor.executemany(
#                         "DELETE FROM memory WHERE dtStamp = ?",
#                         [(row[0],) for row in rows]
#                     )

#         except sqlite3.OperationalError as e:
#             logger.error(f"OperationalError moving '{srcFile}':", exc_info=True)
#         except Exception as e:
#             logger.error(f"Unexpected error moving '{srcFile}':", exc_info=True)

#     # ========== Expiration Actions ==========

#     def removeOldSensory(self, expireUnit, expireValue):
#         self.checkDatabases(
#             self.senDir,
#             lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
#             lambda dbFile, file: os.remove(dbFile),
#             self.getTimedelta(expireUnit, expireValue)
#         )

#     def removeOldInteractionDetails(self, expireUnit, expireValue):
#         self.checkDatabases(
#             self.stmUserInteractionDetails,
#             lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
#             lambda dbFile, file: os.remove(dbFile),
#             self.getTimedelta(expireUnit, expireValue)
#         )

#     def removeOldImageDetails(self, expireUnit, expireValue):
#         self.checkDatabases(
#             self.stmCreatedImageDetails,
#             lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
#             lambda dbFile, file: os.remove(dbFile),
#             self.getTimedelta(expireUnit, expireValue)
#         )

#     def removeOldConversationDetails(self, expireUnit, expireValue):
#         path = self.getDir(self.stmDir, "STM.db")
#         if not path or not os.path.exists(path):
#             return
#         expireThreshold = datetime.now() - self.getTimedelta(expireUnit, expireValue)

#         if not os.path.exists(path):
#             return

#         try:
#             with self.dbLock, sqlite3.connect(path) as conn:
#                 cursor = conn.cursor()
#                 cursor.execute(
#                     "DELETE FROM memory WHERE dtStamp <= ?",
#                     (expireThreshold.isoformat(),)
#                 )
#                 conn.commit()
#         except Exception as e:
#             logger.error(f"Failed to remove old STM records:", exc_info=True)

#     # ========== Archive Actions ==========

#     def archiveConversationDetails(self, expireUnit, expireValue):
#         self.checkDatabases(
#             self.stmUserConversationDetails,
#             lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
#             self.moveConversationDetails,
#             self.getTimedelta(expireUnit, expireValue)
#         )

#     def archiveInteractionDetails(self, expireUnit, expireValue):
#         self.checkDatabases(
#             self.stmUserInteractionDetails,
#             lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
#             self.moveInteractionDetails,
#             self.getTimedelta(expireUnit, expireValue)
#         )

#     def archiveImageDetails(self, expireUnit, expireValue):
#         self.checkDatabases(
#             self.stmCreatedImageDetails,
#             lambda dbFile: datetime.fromtimestamp(os.path.getmtime(dbFile)),
#             self.moveImageDetails,
#             self.getTimedelta(expireUnit, expireValue)
#         )

#     def archiveCreatedImages(self, expireUnit, expireValue):
#         expireDelta = self.getTimedelta(expireUnit, expireValue)
#         if not self.stmCreatedImages or not os.path.exists(self.stmCreatedImages):
#             return
#         for root, _, files in os.walk(self.stmCreatedImages, topdown=False):
#             for file in files:
#                 try:
#                     if not file.lower().endswith(".png"):
#                         continue

#                     filePath = self.getDir(root, file)
#                     fileTime = datetime.fromtimestamp(os.path.getmtime(filePath))

#                     if datetime.now() - fileTime > expireDelta:
#                         relativePath = os.path.relpath(filePath, self.stmCreatedImages)
#                         destPath = self.getDir(self.ltmCreatedImages, relativePath)

#                         os.makedirs(os.path.dirname(destPath), exist_ok=True)
#                         shutil.move(filePath, destPath)

#                 except Exception as e:
#                     logger.error(f"MemoryMaintenance Error archiving image '{file}':", exc_info=True)

#     # ========== Move Helpers ==========

#     def moveConversationDetails(self, dbFile, fileName):
#         if not os.path.exists(dbFile):
#             return

#         userName = os.path.splitext(fileName)[0]
#         ltmPath  = self.getDir(self.ltmUserConversationDetails, "LTM.db")

#         selectQuery = f'''
#             SELECT '{userName}' AS user, dtStamp, content, response FROM memory
#         '''

#         try:
#             with self.dbLock, sqlite3.connect(dbFile) as srcConn:
#                 srcCursor = srcConn.cursor()

#                 # Verify memory table exists
#                 srcCursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory'")
#                 if not srcCursor.fetchone():
#                     return

#                 srcCursor.execute(selectQuery)
#                 rows = srcCursor.fetchall()
#                 if not rows:
#                     return  # 🔥 skip if no rows

#         except Exception as e:
#             logger.error(f"Error pre-checking '{dbFile}':", exc_info=True)
#             return

#         self.createMemoryDatabase(ltmPath)  # only reaches here if data exists

#         self.moveDatabase(
#             srcFile  = dbFile,
#             destFile = ltmPath,
#             createQuery='''
#                 CREATE TABLE IF NOT EXISTS memory (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     user TEXT,
#                     dtStamp TEXT,
#                     content TEXT,
#                     response TEXT
#                 )
#             ''',
#             selectQuery=selectQuery,
#             insertQuery='''
#                 INSERT INTO memory (user, dtStamp, content, response)
#                 VALUES (?, ?, ?, ?)
#             '''
#         )

#     def moveInteractionDetails(self, dbFile, fileName):
#         self.createDetailsDatabase(dbFile)
#         ltmPath = self.getDir(self.ltmUserInteractionDetails, fileName)
#         self.moveDatabase(
#             dbFile,
#             ltmPath,
#             '''CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY AUTOINCREMENT, dtStamp TEXT, content TEXT)''',
#             'SELECT dtStamp, content FROM memory',
#             'INSERT INTO memory (dtStamp, content) VALUES (?, ?)'
#         )

#     def moveImageDetails(self, dbFile, fileName):
#         self.createDetailsDatabase(dbFile)
#         ltmPath = self.getDir(self.ltmCreatedImageDetails, fileName)
#         self.moveDatabase(
#             dbFile,
#             ltmPath,
#             '''CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY AUTOINCREMENT, dtStamp TEXT, content TEXT)''',
#             'SELECT dtStamp, content FROM memory',
#             'INSERT INTO memory (dtStamp, content) VALUES (?, ?)'
#         )



#     # ─── Clear ────────────────────────────────────────────────────────
#     def clearPerception(self):
#         self.perception.clear()
#         print("Perception Feedback Cleared.")

#     def clearFirstEntry(self):
#         self._clearEntryByQuery('MIN')

#     def clearLastEntry(self):
#         self._clearEntryByQuery('MAX')

#     def clearAllEntries(self):
#         user  = self.getCurrentUserName()
#         senDb = self.getDir(self.db.senDir,                     f"{user}.db")
#         stmDb = self.getDir(self.db.stmUserConversationDetails, "STM.db")
#         ltmDb = self.getDir(self.db.ltmUserConversationDetails, "LTM.db")

#         self._deleteByQuery(senDb, "DELETE FROM memory")
#         self._deleteByQuery(stmDb, "DELETE FROM memory WHERE user = ?", [user])
#         self._deleteByQuery(ltmDb, "DELETE FROM memory WHERE user = ?", [user])

#     def _clearEntryByQuery(self, which):  # which: "MIN" or "MAX"
#         user  = self.getCurrentUserName()
#         senDb = self.getDir(self.db.senDir,                     f"{user}.db")
#         stmDb = self.getDir(self.db.stmUserConversationDetails, "STM.db")
#         ltmDb = self.getDir(self.db.ltmUserConversationDetails, "LTM.db")

#         # SEN (no user column)
#         self._deleteByQuery(
#             senDb,
#             f"DELETE FROM memory WHERE id = (SELECT {which}(id) FROM memory)"
#         )

#         # STM + LTM (filter by user)
#         self._deleteByQuery(
#             stmDb,
#             f"DELETE FROM memory WHERE id = (SELECT {which}(id) FROM memory WHERE user = ?) AND user = ?",
#             [user, user]
#         )
#         self._deleteByQuery(
#             ltmDb,
#             f"DELETE FROM memory WHERE id = (SELECT {which}(id) FROM memory WHERE user = ?) AND user = ?",
#             [user, user]
#         )

#     def _deleteByQuery(self, path, query, params=None):
#         if os.path.exists(path):
#             try:
#                 with self.dbLock, sqlite3.connect(path) as conn:
#                     cursor = conn.cursor()
#                     cursor.execute(query, params or [])
#                     conn.commit()
#             except Exception as e:
#                 logger.error(f"Failed to clear from {path}:", exc_info=True)


#     # ─── View ────────────────────────────────────────────────────────
#     def viewDatabase(self, path, limit=None):
#         return self._viewTable(path, "memory", limit)

#     def viewDetailsDatabase(self, path, limit=None):
#         return self._viewTable(path, "memory", limit)

#     def _viewTable(self, path, tableName, limit=None):
#         if not os.path.exists(path):
#             logger.warning(f"Database not found: {path}")
#             return []

#         try:
#             with self.dbLock, sqlite3.connect(path) as conn:
#                 cursor    = conn.cursor()

#                 # Check if table exists
#                 cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tableName}'")
#                 if not cursor.fetchone():
#                     logger.warning(f"No '{tableName}' table in: {path}")
#                     return []

#                 cursor.execute(f"PRAGMA table_info({tableName})")
#                 columns = [col[1] for col in cursor.fetchall()]

#                 query = f"SELECT * FROM {tableName}"
#                 if limit:
#                     query += f" ORDER BY id DESC LIMIT {limit}"

#                 cursor.execute(query)
#                 rows       = cursor.fetchall()
#                 return [dict(zip(columns, row)) for row in rows]

#         except Exception as e:
#             logger.error(f"[Viewer] Error reading {path}:", exc_info=True)
#             return []

