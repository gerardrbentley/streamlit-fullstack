from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from typing import Optional, List
from dataclasses import dataclass, asdict

import streamlit as st

CHAR_LIMIT = 140
DATABASE_URI = "notes.db"


def main() -> None:
    """Main Streamlit App Entry"""
    connection = get_connection(DATABASE_URI)
    init_db(connection)

    st.header(f"The Littlest Fullstack App!")
    render_sidebar(connection)


def render_sidebar(connection: sqlite3.Connection) -> None:
    """Provides Selectbox Drop Down for which view to render"""
    views = {
        "Read Note Feed": render_read,  # Read first for display default
        "Create a Note": render_create,
        "Update a Note": render_update,
        "Delete a Note": render_delete,
        "About": render_about,
    }
    choice = st.sidebar.selectbox("Menu", views.keys())
    render_func = views.get(choice)
    render_func(connection)


@st.cache(hash_funcs={sqlite3.Connection: id}, suppress_st_warning=True)
def get_connection(connection_string: str = ":memory:") -> sqlite3.Connection:
    """Make a connection object to sqlite3 with key-value Rows as outputs
    Threading in Streamlit / Python with sqlite:
    - https://discuss.streamlit.io/t/prediction-analysis-and-creating-a-database/3504/2
    - https://stackoverflow.com/questions/48218065/programmingerror-sqlite-objects-created-in-a-thread-can-only-be-used-in-that-sa
    """
    st.error("Get Connection")
    connection = sqlite3.connect(connection_string, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


@st.cache(hash_funcs={sqlite3.Connection: id}, suppress_st_warning=True)
def init_db(connection: sqlite3.Connection) -> None:
    """Create table and seed data as needed"""
    st.warning("Init DB")
    create_notes_table(connection)
    seed_notes_table(connection)


def create_notes_table(connection: sqlite3.Connection) -> None:
    """Create Notes Table in the database if it doesn't already exist"""
    st.warning("Creating Notes Table")
    init_notes_query = f"""CREATE TABLE IF NOT EXISTS notes(
   created_timestamp INT NOT NULL,
   updated_timestamp INT NOT NULL,
   username VARCHAR({CHAR_LIMIT}) NOT NULL,
   body VARCHAR({CHAR_LIMIT}) NOT NULL);
"""
    execute_query(connection, init_notes_query)


def seed_notes_table(connection: sqlite3.Connection) -> None:
    """Insert a sample Note row into the database"""
    st.warning("Seeding Notes Table")
    new_note = Note(
        rowid=1,
        created_timestamp=1644470272,
        updated_timestamp=utc_timestamp(),
        username="SYSTEM",
        body="Auto Generated Note!!! :tada:",
    )
    st.warning(f"Updating Note #{new_note.rowid}")
    NoteService.update_note(connection, new_note)


def execute_query(
    connection: sqlite3.Connection, query: str, args: Optional[dict] = None
) -> list:
    """Given sqlite3.Connection and a string query (and optionally necessary query args as a dict),
    Attempt to execute query with cursor, commit transaction, and return fetched rows"""
    cur = connection.cursor()
    if args is not None:
        cur.execute(query, args)
    else:
        cur.execute(query)
    connection.commit()
    results = cur.fetchall()
    cur.close()
    return results


@dataclass
class BaseNote:
    """Note Entity for Creation / Handling without database ID"""

    created_timestamp: int
    updated_timestamp: int
    username: str
    body: str


@dataclass
class Note(BaseNote):
    """Note Entity to model database entry"""

    rowid: int


class NoteService:
    """Namespace for Database Related Note Operations"""

    def list_all_notes(
        connection: sqlite3.Connection,
    ) -> List[sqlite3.Row]:
        """Returns rows from all notes. Ordered in reverse creation order"""
        read_notes_query = f"""SELECT rowid, created_timestamp, updated_timestamp, username, body
        FROM notes ORDER BY rowid DESC;"""
        note_rows = execute_query(connection, read_notes_query)
        return note_rows

    def create_note(connection: sqlite3.Connection, note: BaseNote) -> None:
        """Create a Note in the database"""
        create_note_query = f"""INSERT into notes(created_timestamp, updated_timestamp, username, body)
    VALUES(:created_timestamp, :updated_timestamp, :username, :body);"""
        execute_query(connection, create_note_query, asdict(note))

    def update_note(connection: sqlite3.Connection, note: Note) -> None:
        """Replace a Note in the database"""
        update_note_query = f"""UPDATE notes SET updated_timestamp=:updated_timestamp, username=:username, body=:body WHERE rowid=:rowid;"""
        execute_query(connection, update_note_query, asdict(note))

    def delete_note(connection: sqlite3.Connection, note: Note) -> None:
        """Delete a Note in the database"""
        delete_note_query = f"""DELETE from notes WHERE rowid = :rowid;"""
        execute_query(connection, delete_note_query, {"rowid": note.rowid})


def display_timestamp(timestamp: int) -> datetime:
    """Return python datetime from utc timestamp"""
    return datetime.fromtimestamp(timestamp, timezone.utc)


def utc_timestamp() -> int:
    """Return current utc timestamp rounded to nearest int"""
    return int(datetime.utcnow().timestamp())


def render_note(note: Note) -> None:
    """Show a note with streamlit display functions"""
    st.subheader(f"By {note.username} at {display_timestamp(note.created_timestamp)}")
    st.caption(
        f"Note #{note.rowid} -- Updated at {display_timestamp(note.updated_timestamp)}"
    )
    st.write(note.body)


def do_create(connection: sqlite3.Connection, note: BaseNote) -> None:
    """Streamlit callback for creating a note and showing confirmation"""
    st.warning("Creating a Note")
    NoteService.create_note(connection, note)
    st.success("Created a Note")


def render_create(connection: sqlite3.Connection) -> None:
    """Show the form for creating a new Note"""
    with st.form("create_form"):
        st.write("Enter a Username and Note")
        username = st.text_input(
            "Username",
            value="anonymous",
            max_chars=CHAR_LIMIT,
            help="Enter a Username to display by your note",
        )
        note = st.text_input(
            "Note",
            value="Sample Note Input",
            max_chars=CHAR_LIMIT,
            help="Enter your note (valid html-safe Markdown)",
        )

        new_note = BaseNote(utc_timestamp(), utc_timestamp(), username, note)
        submitted = st.form_submit_button("Submit", help="Create your Note!")
        if submitted:
            do_create(connection, new_note)


def render_read(connection: sqlite3.Connection) -> None:
    """Show all of the notes in the database in a feed"""
    st.success("Reading Note Feed")
    note_rows = NoteService.list_all_notes(connection)
    with st.expander("Raw Note Table Data"):
        st.table(note_rows)

    notes = [Note(**row) for row in note_rows]
    for note in notes:
        render_note(note)


def do_update(connection: sqlite3.Connection, new_note: Note) -> None:
    """Streamlit callback for updating a note and showing confirmation"""
    st.warning(f"Updating Note #{new_note.rowid} {new_note}")
    NoteService.update_note(connection, new_note)
    st.success(f"Updated Note #{new_note.rowid} {new_note}")


def render_update(connection: sqlite3.Connection) -> None:
    """Show the form for updating an existing Note"""
    st.success("Reading Notes")
    note_rows = NoteService.list_all_notes(connection)
    notes = [Note(**row) for row in note_rows]
    note_map = {
        f"{note.rowid} - by {note.username} on {display_timestamp(note.created_timestamp)}": note
        for note in notes
    }
    note_id = st.selectbox("Which Note to Update?", note_map.keys())
    note_to_update = note_map[note_id]
    with st.form("update_form"):
        st.write("Update Username and/or Note")
        username = st.text_input(
            "Username",
            value=note_to_update.body,
            max_chars=CHAR_LIMIT,
            help="Enter a Username to display by your note",
        )
        body = st.text_input(
            "Note",
            value=note_to_update.username,
            max_chars=CHAR_LIMIT,
            help="Enter your note (valid html-safe Markdown)",
        )

        st.caption(f"Note #{note_id}")

        submitted = st.form_submit_button(
            "Submit",
            help="This will change the body of the note, the username, or both. It also updates the updated at time.",
        )
        if submitted:
            new_note = Note(
                note_to_update.created_timestamp,
                utc_timestamp(),
                username,
                body,
                note_to_update.rowid,
            )
            do_update(connection, new_note)


def do_delete(connection: sqlite3.Connection, note_to_delete: Note) -> None:
    """Streamlit callback for deleting a note and showing confirmation"""
    st.warning(f"Deleting Note #{note_to_delete.rowid}")
    NoteService.delete_note(connection, note_to_delete)
    st.success(f"Deleted Note #{note_to_delete.rowid}")


def render_delete(connection: sqlite3.Connection) -> None:
    """Show the form for deleting an existing Note"""
    st.success("Reading Notes")
    note_rows = NoteService.list_all_notes(connection)
    note_map = {row["rowid"]: Note(**row) for row in note_rows}
    note_id = st.selectbox("Which Note to Delete?", note_map.keys())
    note_to_delete = note_map[note_id]

    render_note(note_to_delete)

    st.button(
        "Delete Note (This Can't Be Undone!)",
        help="I hope you know what you're getting into!",
        on_click=do_delete,
        args=(connection, note_to_delete),
    )


def render_about(*_) -> None:
    """Show the README info"""
    st.write(Path("README.md").read_text())


if __name__ == "__main__":
    main()
