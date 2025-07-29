"""ZODB wrapper as singleton.
"""

from ZODB import FileStorage, DB
import transaction


class Borg:
    """Singelton with shared state.
    """
    # No public methods.
    # pylint: disable-msg=R0903
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state


class SharedDB(Borg):
    """Shared database.
    """
    def __init__(self):
        Borg.__init__(self)

    def open(self, db_file_name):
        """Open the database.
        """
        storage = FileStorage.FileStorage(db_file_name)
        self.db = DB(storage)
        try:
            self.db.pack()
        #  Dynamic member.
        # pylint: disable-msg=E1101
        except FileStorage.FileStorageError:
            pass
        self.connection = self.db.open()
        self.root = self.connection.root()
        self.is_open = True

    def close(self):
        """Close the database.
        """
        if self.is_open:
            transaction.commit()
            self.connection.close()
            self.db.close()
            self.is_open = False
