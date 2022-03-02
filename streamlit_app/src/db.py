from dataclasses import asdict
from typing import List, Optional, Type
import logging

import httpx
import psycopg
from psycopg.rows import class_row
from pydantic import BaseSettings

from src.data import Note
from src.data import Note, BaseNote
from src.formatting import utc_timestamp


CHAR_LIMIT = 140
DATABASE_URI = "notes.db"


class PsycopgSettings(BaseSettings):
    """\
host:
    Name of host to connect to. If this begins with a slash, it specifies Unix-domain communication rather than TCP/IP communication; the value is the name of the directory in which the socket file is stored. The default behavior when host is not specified is to connect to a Unix-domain socket in /tmp (or whatever socket directory was specified when PostgreSQL was built). On machines without Unix-domain sockets, the default is to connect to localhost.

port:
    Port number to connect to at the server host, or socket file name extension for Unix-domain connections.

dbname:
    The database name. Defaults to be the same as the user name.

user:
    PostgreSQL user name to connect as. Defaults to be the same as the operating system name of the user running the application.

password:
    Password to be used if the server demands password authentication.
"""

    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: str

    def get_connection_string(self) -> str:
        return f"dbname={self.postgres_db} host={self.postgres_host} user={self.postgres_user} password={self.postgres_password}"

    def get_connection_args(self) -> dict:
        return {
            "host": self.postgres_host,
            "port": self.postgres_port,
            "dbname": self.postgres_db,
            "user": self.postgres_user,
            "password": self.postgres_password,
        }


def create_notes_table(connection: psycopg.Connection) -> None:
    """Create Notes Table in the database if it doesn't already exist"""
    init_notes_query = f"""CREATE TABLE IF NOT EXISTS notes(
    rowid serial PRIMARY KEY,
    created_timestamp bigint NOT NULL,
    updated_timestamp bigint NOT NULL,
    username varchar({CHAR_LIMIT}) NOT NULL,
    body varchar({CHAR_LIMIT}) NOT NULL);
"""
    execute_query(connection, init_notes_query)


def seed_notes_table(connection: psycopg.Connection) -> None:
    """Insert a sample Note row into the database"""
    seed_note = Note(
        rowid=1,
        created_timestamp=1644470272,
        updated_timestamp=utc_timestamp(),
        username="SYSTEM",
        body="Auto Generated Note!!! :tada:",
    )
    seed_note_query = f"""INSERT into notes(rowid, created_timestamp, updated_timestamp, username, body)
    VALUES(%(rowid)s, %(created_timestamp)s, %(updated_timestamp)s, %(username)s, %(body)s)
    ON CONFLICT DO NOTHING;"""
    execute_query(connection, seed_note_query, asdict(seed_note))
    # Reset autoincrement
    reset_seq_query = """SELECT setval('notes_rowid_seq', (SELECT MAX(rowid) from "notes"));"""
    execute_query(connection, reset_seq_query)


def fetch_rows(
    connection: psycopg.Connection,
    query: str,
    args: Optional[dict] = None,
    dclass: Optional[Type] = None,
) -> list:
    """Given psycopg.Connection and a string query (and optionally necessary query args as a dict),
    Attempt to execute query with cursor, commit transaction, and return fetched rows"""
    if dclass is not None:
        cur = connection.cursor(row_factory=class_row(dclass))
    else:
        cur = connection.cursor()
    if args is not None:
        cur.execute(query, args)
    else:
        cur.execute(query)
    results = cur.fetchall()
    cur.close()
    return results


def execute_query(
    connection: psycopg.Connection,
    query: str,
    args: Optional[dict] = None,
) -> None:
    """Given psycopg.Connection and a string query (and optionally necessary query args as a dict),
    Attempt to execute query with cursor"""
    cur = connection.cursor()
    if args is not None:
        cur.execute(query, args)
    else:
        cur.execute(query)
    cur.close()


class NoteService:
    """Namespace for Database Related Note Operations"""

    def list_all_notes() -> List[Note]:
        response = httpx.get("http://backend:3000/notes")
        logging.info(response)
        json_notes = response.json()
        notes = [Note(**note) for note in json_notes['notes']]
        return notes

    def create_note(note: BaseNote) -> None:
        """Create a Note in the database"""
        response = httpx.post("http://backend:3000/notes", json=asdict(note))
        return response

    def update_note(note: Note) -> None:
        """Replace a Note in the database"""
        response = httpx.put(f"http://backend:3000/notes/{note.rowid}", json=asdict(note))
        return response

    def delete_note(note: Note) -> None:
        """Delete a Note in the database"""
        # DELETE spec doesn't include json body: https://github.com/encode/httpx/discussions/1587
        response = httpx.request(method="delete", url=f"http://backend:3000/notes/{note.rowid}", json=asdict(note))
        return response
