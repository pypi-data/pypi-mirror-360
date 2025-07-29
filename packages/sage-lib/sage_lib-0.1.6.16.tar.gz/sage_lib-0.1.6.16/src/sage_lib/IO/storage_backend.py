# storage_backend.py
import sqlite3, pickle
from typing import List
from abc import ABC, abstractmethod

class StorageBackend(ABC):
    """
    Abstract interface for container storage backends.
    """
    @abstractmethod
    def add(self, obj) -> int:
        """Store object and return its ID."""
        raise NotImplementedError("add must be implemented by subclasses")

    @abstractmethod
    def get(self, obj_id: int):
        """Retrieve object by ID."""
        raise NotImplementedError("get must be implemented by subclasses")

    @abstractmethod
    def remove(self, obj_id: int) -> None:
        """Delete object by ID."""
        raise NotImplementedError("remove must be implemented by subclasses")

    @abstractmethod
    def list_ids(self) -> List[int]:
        """Return list of all object IDs."""
        raise NotImplementedError("list_ids must be implemented by subclasses")

    @abstractmethod
    def count(self) -> int:
        """Return total number of stored objects."""
        raise NotImplementedError("count must be implemented by subclasses")

class MemoryStorage(StorageBackend):
    """
    In-memory storage using a Python list.
    """
    def __init__(self):
        self._data: List = []

    def add(self, obj) -> int:
        self._data.append(obj)
        return len(self._data) - 1

    def get(self, obj_id: int):
        try:
            return self._data[obj_id]
        except IndexError:
            raise KeyError(f"No object found with id {obj_id}")

    def set(self, obj_list: list):
        try:
            self._data = obj_list
            return len(self._data) - 1
        except IndexError:
            raise KeyError(f"Error in set data {obj_id}")

    def remove(self, obj_id: int) -> None:
        try:
            del self._data[obj_id]
        except IndexError:
            raise KeyError(f"No object found with id {obj_id}")

    def list_ids(self) -> List[int]:
        return list(range(len(self._data)))

    def count(self) -> int:
        return len(self._data)

class SQLiteStorage(StorageBackend):
    """
    SQLite-based storage, pickling objects into a BLOB.
    """
    def __init__(self, db_path: str):
        # ensure directory exists
        import os
        dir_path = os.path.dirname(db_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS containers (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                data BLOB NOT NULL
            );
            """
        )
        self.conn.commit()

    def add(self, obj) -> int:
        blob = pickle.dumps(obj)
        cur = self.conn.cursor()
        cur.execute("INSERT INTO containers (data) VALUES (?);", (blob,))
        self.conn.commit()
        return cur.lastrowid

    def get(self, obj_id: int):
        cur = self.conn.cursor()
        cur.execute("SELECT data FROM containers WHERE id = ?;", (obj_id,))
        row = cur.fetchone()
        if row is None:
            raise KeyError(f"No container with id {obj_id}")
        return pickle.loads(row[0])

    def remove(self, obj_id: int) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM containers WHERE id = ?;", (obj_id,))
        if cur.rowcount == 0:
            raise KeyError(f"No container with id {obj_id}")
        self.conn.commit()

    def list_ids(self) -> List[int]:
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM containers;")
        return [row[0] for row in cur.fetchall()]

    def count(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM containers;")
        return cur.fetchone()[0]
