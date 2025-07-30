
import os
import sqlite3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ClearMemory:
    def __init__(self, dbLock, db, getCurrentUserName):
        self.dbLock   = dbLock
        self.db       = db
        self.userName = getCurrentUserName

    def getDir(self, *paths):
        return str(Path(*paths).resolve())

    def clearFirstEntry(self):
        self._clearEntryByQuery('MIN')

    def clearLastEntry(self):
        self._clearEntryByQuery('MAX')

    def clearAllEntries(self):
        user  = self.userName()
        senDb = self.getDir(self.db.senDir,                     f"{user}.db")
        stmDb = self.getDir(self.db.stmUserConversationDetails, "STM.db")
        ltmDb = self.getDir(self.db.ltmUserConversationDetails, "LTM.db")

        self._deleteByQuery(senDb, "DELETE FROM memory")
        self._deleteByQuery(stmDb, "DELETE FROM memory WHERE user = ? COLLATE NOCASE", [user])
        self._deleteByQuery(ltmDb, "DELETE FROM memory WHERE user = ? COLLATE NOCASE", [user])

    def _clearEntryByQuery(self, which):  # which: "MIN" or "MAX"
        user  = self.userName()
        senDb = self.getDir(self.db.senDir,                     f"{user}.db")
        stmDb = self.getDir(self.db.stmUserConversationDetails, "STM.db")
        ltmDb = self.getDir(self.db.ltmUserConversationDetails, "LTM.db")

        # SEN (no user column)
        self._deleteByQuery(
            senDb,
            f"DELETE FROM memory WHERE id = (SELECT {which}(id) FROM memory)"
        )

        # STM + LTM (filter by user, case-insensitive)
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

    def _deleteByQuery(self, dbPath, query, params=None):
        if os.path.exists(dbPath):
            try:
                with self.dbLock, sqlite3.connect(dbPath) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params or [])
                    conn.commit()
            except Exception as e:
                logger.error(f"Failed to clear from {dbPath}:", exc_info=True)













# import os
# import sqlite3
# from pathlib import Path
# import logging

# logger = logging.getLogger(__name__)


# class ClearMemory:
#     def __init__(self, dbLock, db, getCurrentUserName):
#         self.dbLock             = dbLock
#         self.db                 = db
#         self.userName = getCurrentUserName

#     def getDir(self, *paths):
#         return str(Path(*paths).resolve())

#     def clearFirstEntry(self):
#         self._clearEntryByQuery('MIN')

#     def clearLastEntry(self):
#         self._clearEntryByQuery('MAX')

#     def clearAllEntries(self):
#         user  = self.userName()
#         senDb = self.getDir(self.db.senDir,                     f"{user}.db")
#         stmDb = self.getDir(self.db.stmUserConversationDetails, "STM.db")
#         ltmDb = self.getDir(self.db.ltmUserConversationDetails, "LTM.db")

#         self._deleteByQuery(senDb, "DELETE FROM memory")
#         self._deleteByQuery(stmDb, "DELETE FROM memory WHERE user = ?", [user])
#         self._deleteByQuery(ltmDb, "DELETE FROM memory WHERE user = ?", [user])

#     def _clearEntryByQuery(self, which):  # which: "MIN" or "MAX"
#         user  = self.userName()
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

#     def _deleteByQuery(self, dbPath, query, params=None):
#         if os.path.exists(dbPath):
#             try:
#                 with self.dbLock, sqlite3.connect(dbPath) as conn:
#                     cursor = conn.cursor()
#                     cursor.execute(query, params or [])
#                     conn.commit()
#             except Exception as e:
#                 logger.error(f"Failed to clear from {dbPath}:", exc_info=True)

