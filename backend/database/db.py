import sqlite3
from pathlib import Path

from backend.core.config import DB_PATH

# created_at localtime: uygulama tek makinede calisiyor, arayuzde UTC gostermek
# kullaniciyi yaniltiyordu (saat farki kadar geride goruluyordu)
SCHEMA = """
CREATE TABLE IF NOT EXISTS collections (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS documents (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    filename      TEXT NOT NULL,
    file_type     TEXT NOT NULL,
    char_count    INTEGER NOT NULL,
    word_count    INTEGER NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS chunks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text  TEXT NOT NULL,
    start_char  INTEGER NOT NULL,
    end_char    INTEGER NOT NULL,
    embedding   BLOB,
    UNIQUE (document_id, chunk_index)
);

CREATE TABLE IF NOT EXISTS chat_history (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER REFERENCES collections(id) ON DELETE CASCADE,
    question      TEXT NOT NULL,
    answer        TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS feedback (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id    INTEGER NOT NULL REFERENCES chat_history(id) ON DELETE CASCADE,
    rating     INTEGER NOT NULL CHECK (rating IN (-1, 1)),
    comment    TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_documents_collection ON documents(collection_id);
CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_collection ON chat_history(collection_id);
CREATE INDEX IF NOT EXISTS idx_feedback_chat ON feedback(chat_id);
"""


def get_connection(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    # sqlite'ta yabanci anahtar kontrolu baglanti basina kapali gelir
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(db_path: str | Path = DB_PATH) -> None:
    connection = get_connection(db_path)
    try:
        connection.executescript(SCHEMA)
        connection.commit()
    finally:
        connection.close()
