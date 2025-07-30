
import os
import sqlite3
import threading
from datetime import datetime
from PIL import Image
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class RetrieveMemory:
    def __init__(self, dbLock):
        self.dbLock       = dbLock
        self.sessionStart = datetime.now()

    def getDir(self, *paths):
        return str(Path(*paths).resolve())

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
            except sqlite3.OperationalError as e:
                logger.error(f"OperationalError while retrieving data from {dbFile}:", exc_info=True)
            except Exception as e:
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

    def retrieveSensory(self, user, path):
        dbFile = self.getDir(path, f"{user()}.db")
        query  = 'SELECT dtStamp, content, response FROM memory'
        params = []
        return self.retrieveMemoryFromDb(dbFile, query, params)

    def retrieveConversationDetails(self, user, path1, path2, startDate=None, endDate=None):
        stmDb = self.getDir(path1, "STM.db")
        ltmDb = self.getDir(path2, "LTM.db")
        query  = 'SELECT dtStamp, content, response FROM memory WHERE user = ? COLLATE NOCASE'
        params = [user]
        if startDate:
            startDate = self.formatIsoDate(startDate)
            query     += ' AND dtStamp >= ?'
            params.append(startDate)
        if endDate:
            endDate = self.formatIsoDate(endDate)
            query   += ' AND dtStamp <= ?'
            params.append(endDate)
        memory = self.retrieveMemoryFromDb(stmDb, query, params)
        memory += self.retrieveMemoryFromDb(ltmDb, query, params)
        return memory

    def retrieveInteractionDetails(self, path1, path2, startDate=None, endDate=None):
        stmDetailsDb = self.getDir(path1, "Details.db")
        ltmDetailsDb = self.getDir(path2, "Details.db")
        query  = 'SELECT dtStamp, content FROM memory WHERE 1=1'
        params = []
        if startDate:
            startDate = self.formatIsoDate(startDate)
            query     += ' AND dtStamp >= ?'
            params.append(startDate)
        if endDate:
            endDate = self.formatIsoDate(endDate)
            query   += ' AND dtStamp <= ?'
            params.append(endDate)
        memory = self.retrieveDetailsFromDb(stmDetailsDb, query, params)
        memory += self.retrieveDetailsFromDb(ltmDetailsDb, query, params)
        return memory

    def retrieveLastInteractionTime(self, user, path1, path2, path3):
        dbSources = [
            (self.getDir(path1, f"{user}.db"),
             'SELECT dtStamp FROM memory ORDER BY dtStamp DESC LIMIT 1', []),
            (self.getDir(path2, "STM.db"),
             'SELECT dtStamp FROM memory WHERE user = ? COLLATE NOCASE ORDER BY dtStamp DESC LIMIT 1', [user]),
            (self.getDir(path3, "LTM.db"),
             'SELECT dtStamp FROM memory WHERE user = ? COLLATE NOCASE ORDER BY dtStamp DESC LIMIT 1', [user])
        ]
        for dbPath, query, params in dbSources:
            timestamps = self.retrieveMemoryFromDb(
                dbPath, query, params, returnTimestampOnly=True
            )
            if timestamps:
                try:
                    return datetime.now() - datetime.fromisoformat(timestamps[0])
                except ValueError:
                    logger.warning(f"Invalid timestamp in DB: {timestamps[0]}")
        return datetime.now() - self.sessionStart

    def retrieveLastInteractionDate(self, user, path1, path2, path3):
        dbSources = [
            (self.getDir(path1, f"{user}.db"),
             'SELECT dtStamp FROM memory ORDER BY dtStamp DESC LIMIT 1', []),
            (self.getDir(path2, "STM.db"),
             'SELECT dtStamp FROM memory WHERE user = ? COLLATE NOCASE ORDER BY dtStamp DESC LIMIT 1', [user]),
            (self.getDir(path3, "LTM.db"),
             'SELECT dtStamp FROM memory WHERE user = ? COLLATE NOCASE ORDER BY dtStamp DESC LIMIT 1', [user])
        ]
        for dbPath, query, params in dbSources:
            timestamps = self.retrieveMemoryFromDb(
                dbPath, query, params, returnTimestampOnly=True
            )
            if timestamps:
                try:
                    return datetime.fromisoformat(timestamps[0])
                except ValueError:
                    logger.warning(f"Invalid timestamp in DB: {timestamps[0]}")
        return self.sessionStart

    def retrieveImageDetails(self, path1, path2, startDate=None, endDate=None):
        stmDetailsDb = self.getDir(path1, "Details.db")
        ltmDetailsDb = self.getDir(path2, "Details.db")
        query  = 'SELECT dtStamp, content FROM memory WHERE 1=1'
        params = []
        if startDate:
            startDate = self.formatIsoDate(startDate)
            query     += ' AND dtStamp >= ?'
            params.append(startDate)
        if endDate:
            endDate = self.formatIsoDate(endDate)
            query   += ' AND dtStamp <= ?'
            params.append(endDate)
        memory = self.retrieveDetailsFromDb(stmDetailsDb, query, params)
        memory += self.retrieveDetailsFromDb(ltmDetailsDb, query, params)
        return memory

    def retrieveCreatedImage(self, path, imageName):
        imagePath = self.getImageDir(path, f"{imageName}.png")
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
















# import os
# import sqlite3
# import threading
# from datetime import datetime, timedelta
# from functools import partial
# import shutil
# import time
# from PIL import Image
# from io import BytesIO
# from pathlib import Path
# import logging

# logger = logging.getLogger(__name__)


# class RetrieveMemory:
#     def __init__(self, dbLock):
#         self.dbLock       = dbLock
#         self.sessionStart = datetime.now()

#     def getDir(self, *paths):
#         return str(Path(*paths).resolve())

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

#     def retrieveSensory(self, user, path):
#         dbFile = self.getDir(path, f"{user()}.db")
#         query  = 'SELECT dtStamp, content, response FROM memory'
#         params = []
#         return self.retrieveMemoryFromDb(dbFile, query, params)

#     def retrieveConversationDetails(self, user, path1, path2, startDate=None, endDate=None):
#         stmDb = self.getDir(path1, "STM.db")
#         ltmDb = self.getDir(path2, "LTM.db")

#         query  = 'SELECT dtStamp, content, response FROM memory WHERE user = ?'
#         params = [user]

#         if startDate:
#             startDate = self.formatIsoDate(startDate)
#             query     += ' AND dtStamp >= ?'
#             params.append(startDate)
#         if endDate:
#             endDate = self.formatIsoDate(endDate)
#             query   += ' AND dtStamp <= ?'
#             params.append(endDate)

#         memory = self.retrieveMemoryFromDb(stmDb, query, params)
#         memory += self.retrieveMemoryFromDb(ltmDb, query, params)
#         return memory

#     def retrieveInteractionDetails(self, path1, path2, startDate=None, endDate=None):
#         stmDetailsDb = self.getDir(path1, "Details.db")
#         ltmDetailsDb = self.getDir(path2, "Details.db")

#         query  = 'SELECT dtStamp, content FROM memory WHERE 1=1'
#         params = []

#         if startDate:
#             startDate = self.formatIsoDate(startDate)
#             query     += ' AND dtStamp >= ?'
#             params.append(startDate)
#         if endDate:
#             endDate = self.formatIsoDate(endDate)
#             query   += ' AND dtStamp <= ?'
#             params.append(endDate)

#         memory = self.retrieveDetailsFromDb(stmDetailsDb, query, params)
#         memory += self.retrieveDetailsFromDb(ltmDetailsDb, query, params)
#         return memory

#     def retrieveLastInteractionTime(self, user, path1, path2, path3):
#         userCapitalized  = user.capitalize()

#         dbSources = [
#             (self.getDir(path1, f"{userCapitalized}.db"),
#              'SELECT dtStamp FROM memory ORDER BY dtStamp DESC LIMIT 1', []),
#             (self.getDir(path2, "STM.db"),
#              'SELECT dtStamp FROM memory WHERE user = ? ORDER BY dtStamp DESC LIMIT 1', [user]),
#             (self.getDir(path3, "LTM.db"),
#              'SELECT dtStamp FROM memory WHERE user = ? ORDER BY dtStamp DESC LIMIT 1', [user])
#         ]

#         for dbPath, query, params in dbSources:
#             timestamps = self.retrieveMemoryFromDb(
#                 dbPath, query, params, returnTimestampOnly=True
#             )
#             if timestamps:
#                 try:
#                     return datetime.now() - datetime.fromisoformat(timestamps[0])
#                 except ValueError:
#                     logger.warning(f"Invalid timestamp in DB: {timestamps[0]}")

#         return datetime.now() - self.sessionStart


#     def retrieveLastInteractionDate(self, user, path1, path2, path3):
#         userCapitalized  = user.capitalize()

#         dbSources = [
#             (self.getDir(path1, f"{userCapitalized}.db"),
#              'SELECT dtStamp FROM memory ORDER BY dtStamp DESC LIMIT 1', []),
#             (self.getDir(path2, "STM.db"),
#              'SELECT dtStamp FROM memory WHERE user = ? ORDER BY dtStamp DESC LIMIT 1', [user]),
#             (self.getDir(path3, "LTM.db"),
#              'SELECT dtStamp FROM memory WHERE user = ? ORDER BY dtStamp DESC LIMIT 1', [user])
#         ]

#         for dbPath, query, params in dbSources:
#             timestamps = self.retrieveMemoryFromDb(
#                 dbPath, query, params, returnTimestampOnly=True
#             )
#             if timestamps:
#                 try:
#                     return datetime.fromisoformat(timestamps[0])
#                 except ValueError:
#                     logger.warning(f"Invalid timestamp in DB: {timestamps[0]}")

#         return self.sessionStart

#     def retrieveImageDetails(self, path1, path2, startDate=None, endDate=None):
#         stmDetailsDb = self.getDir(path1, "Details.db")
#         ltmDetailsDb = self.getDir(path2, "Details.db")

#         query  = 'SELECT dtStamp, content FROM memory WHERE 1=1'
#         params = []

#         if startDate:
#             startDate = self.formatIsoDate(startDate)
#             query     += ' AND dtStamp >= ?'
#             params.append(startDate)
#         if endDate:
#             endDate = self.formatIsoDate(endDate)
#             query   += ' AND dtStamp <= ?'
#             params.append(endDate)

#         memory = self.retrieveDetailsFromDb(stmDetailsDb, query, params)
#         memory += self.retrieveDetailsFromDb(ltmDetailsDb, query, params)
#         return memory

#     def retrieveCreatedImage(self, path, imageName):
#         imagePath = self.getImageDir(path, f"{imageName}.png")
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



