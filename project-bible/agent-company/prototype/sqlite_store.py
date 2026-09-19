"""Versioned local fixture store. Not encrypted and not a production audit vault."""
from contextlib import contextmanager
from pathlib import Path
import hashlib
import json
import os
import sqlite3


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class VersionConflict(Exception):
    pass


class Transaction:
    def __init__(self, connection):
        self.connection = connection

    def get(self, namespace, key):
        row = self.connection.execute(
            "SELECT body,version FROM objects WHERE namespace=? AND key=?", (namespace, key)).fetchone()
        return (json.loads(row[0]), row[1]) if row else (None, 0)

    def scan(self, namespace):
        return [(key, json.loads(body), version) for key, body, version in self.connection.execute(
            "SELECT key,body,version FROM objects WHERE namespace=? ORDER BY key", (namespace,))]

    def put(self, namespace, key, value, expected_version):
        old, version = self.get(namespace, key)
        if version != expected_version:
            raise VersionConflict("version_conflict")
        body = canonical(value)
        if version and canonical(old) == body:
            return version
        if version:
            self.connection.execute(
                "UPDATE objects SET body=?,version=version+1 WHERE namespace=? AND key=? AND version=?",
                (body, namespace, key, version))
        else:
            self.connection.execute("INSERT INTO objects VALUES(?,?,1,?)", (namespace, key, body))
        return version + 1

    def event(self, timestamp, kind, value):
        self.connection.execute("INSERT INTO events(at,kind,body) VALUES(?,?,?)",
                                (timestamp, kind, canonical(value)))


class Store:
    """One SQLite write transaction covers state, request receipt and audit event."""
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.before_commit = None  # Test-only failure injection; never exposed over HTTP.
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd)
        except FileExistsError:
            if not self.path.is_file():
                raise ValueError("store_path_not_file")
        connection = self.connect()
        try:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            app_id = connection.execute("PRAGMA application_id").fetchone()[0]
            tables = connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            if version not in (0, 1) or (version == 0 and tables) or (version == 1 and app_id != 0x41434931):
                raise ValueError("unsupported_store_schema")
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("CREATE TABLE IF NOT EXISTS objects(namespace TEXT NOT NULL,key TEXT NOT NULL,"
                               "version INTEGER NOT NULL CHECK(version>0),body TEXT NOT NULL,PRIMARY KEY(namespace,key))")
            connection.execute("CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,"
                               "at REAL NOT NULL,kind TEXT NOT NULL,body TEXT NOT NULL)")
            connection.execute("PRAGMA user_version=1")
            connection.execute("PRAGMA application_id=1094928689")
            connection.commit()
        finally:
            connection.close()

    def connect(self):
        connection = sqlite3.connect(str(self.path), timeout=5, isolation_level=None)
        connection.execute("PRAGMA synchronous=FULL")
        return connection

    @contextmanager
    def transaction(self):
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield Transaction(connection)
            if self.before_commit:
                self.before_commit()
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def backup(self, destination):
        """Offline operator action; refuses overwrite. Restore only in an isolated test."""
        destination = Path(destination).resolve()
        fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(fd)
        source = self.connect()
        target = sqlite3.connect(str(destination))
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()
        return destination
