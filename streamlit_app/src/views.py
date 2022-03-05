import streamlit as st

from src.formatting import display_timestamp, utc_timestamp
from src.models import Note, BaseNote
from src.services import NoteService, CHAR_LIMIT


def render_note(note: Note) -> None:
    """Show a note with streamlit display functions"""
    st.subheader(f"By {note.username} at {display_timestamp(note.created_timestamp)}")
    st.caption(
        f"Note #{note.rowid} -- Updated at {display_timestamp(note.updated_timestamp)}"
    )
    st.write(note.body)


def do_create(note: BaseNote) -> None:
    """Streamlit callback for creating a note and showing confirmation"""
    st.warning("Creating your Note")
    NoteService.create_note(note)
    st.success(
        f"Successfully Created your Note! Check the Read Note Feed page to see it"
    )


def render_create() -> None:
    """Show the form for creating a new Note"""
    with st.form("create_form", clear_on_submit=False):
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
        submitted = st.form_submit_button(
            "Submit", help="Create your Note! (You'll get a confirmation below)"
        )
        if submitted:
            do_create(new_note)


def render_read() -> None:
    """Show all of the notes in the database in a feed"""
    st.success("Reading Note Feed")
    notes = NoteService.list_all_notes()
    with st.expander("Raw Note Table Data"):
        st.table(notes)

    for note in notes:
        render_note(note)


def do_update(new_note: Note) -> None:
    """Streamlit callback for updating a note and showing confirmation"""
    st.warning(f"Updating Note #{new_note.rowid}")
    NoteService.update_note(new_note)
    st.success(f"Updated Note #{new_note.rowid}, go to the Read Notes Feed to see it!")


def render_update() -> None:
    """Show the form for updating an existing Note"""
    st.success("Reading Notes")
    notes = NoteService.list_all_notes()
    note_map = {note.rowid: note for note in notes}
    note_id = st.selectbox(
        "Which Note to Update?",
        note_map.keys(),
        format_func=lambda x: f"{note_map[x].rowid} - by {note_map[x].username} on {display_timestamp(note_map[x].created_timestamp)}",
    )
    note_to_update = note_map[note_id]
    with st.form("update_form"):
        st.write("Update Username and/or Note")
        username = st.text_input(
            "Username",
            value=note_to_update.username,
            max_chars=CHAR_LIMIT,
            help="Enter a Username to display by your note",
        )
        body = st.text_input(
            "Note",
            value=note_to_update.body,
            max_chars=CHAR_LIMIT,
            help="Enter your note (valid html-safe Markdown)",
        )

        st.caption(
            f"Note #{note_id} - by {note_to_update.username} on {display_timestamp(note_to_update.created_timestamp)}"
        )

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
            do_update(new_note)


def do_delete(note_to_delete: Note) -> None:
    """Streamlit callback for deleting a note and showing confirmation"""
    st.warning(f"Deleting Note #{note_to_delete.rowid}")
    NoteService.delete_note(note_to_delete)
    st.success(f"Deleted Note #{note_to_delete.rowid}")


def render_delete() -> None:
    """Show the form for deleting an existing Note"""
    st.success("Reading Notes")
    notes = NoteService.list_all_notes()
    note_map = {note.rowid: note for note in notes}
    note_id = st.selectbox("Which Note to Delete?", note_map.keys())
    note_to_delete = note_map[note_id]

    render_note(note_to_delete)

    st.button(
        "Delete Note (This Can't Be Undone!)",
        help="I hope you know what you're getting into!",
        on_click=do_delete,
        args=(note_to_delete,),
    )


def render_about(*_) -> None:
    """Show App info"""
    st.write("""\
# Streamlit App Demo

Howdy :wave:!
Welcome to my Streamlit Full Stack App exploration.

This started as the Littlest Fullstack App with just Streamlit + SQLite.

Next steps were upgrading the data store to Postgres :elephant:.

Then an NGINX webserver + Docker containerization layer to serve it all up!

Finally a backend REST API layer with Go!""")
