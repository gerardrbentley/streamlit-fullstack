# Streamlit Full Stack App

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/gerardrbentley/streamlit-fullstack/app.py)

Demo Repo on building a Full Stack CRUD App with Streamlit.

Create, Read, Update, and Delete from a feed of 140 character markdown notes.

Ran with `python 3.9.7`, `streamlit 1.4 & 1.5`:

```sh
wget https://raw.githubusercontent.com/gerardrbentley/streamlit-fullstack/littlest/app.py
pip install streamlit
streamlit run app.py
```

(Don't have Python / `pip` installed? [here's my way](https://tech.gerardbentley.com/python/beginner/2022/01/29/install-python.html))

- :mouse: littlest (original) version wil remain on [branch `littlest`](https://github.com/gerardrbentley/streamlit-fullstack/tree/littlest)
- :elephant: Postgres (`psycopg3`) + Nginx + Docker-Compose version at [branch `psycopg`](https://github.com/gerardrbentley/streamlit-fullstack/tree/psycopg) and Live at [streamlit-postgres.gerardbentley.com](https://streamlit-postgres.gerardbentley.com)

## The Littlest Full Stack App

The idea for this was starting with built-in sqlite module and streamlit to build a full stack application in a single Python file:

- Streamlit:
    - Frontend
    - Backend
- SQLite
    - Data Store

Obviously this takes some liberties with the definition of Full-Stack App, for my purposes I take it to mean "a web application with a frontend that receives data upon request to a backend and that data is persisted in some data store"

For the first swing at this I also took the standard CRUD definition of Full-Stack:

- Create
- Read
- Update
- Delete

### Data Store

Using SQLite is straightforward if you understand how to set up and query other SQL flavors.

I say this because we don't need to download or spin up any external database server, its a C library that will let us interact with a database with just two lines of python!

```python
import sqlite3
connection = sqlite3.connect(':memory')
```

This gets us a `Connection` object for interacting with an in-memory SQL database!

For the purposes of using it as a more persistant store, it can be configured to write to a local file (conventionally ending with `.db`).

It also defaults to only being accessible by a single thread, so we'll need to turn this off for multiple users

```python
connection = sqlite3.connect('notes.db', check_same_thread=False)
```

### Backend

This is all in one file, but the idea of a "Service" that provides access to the data store and returns rows from the data store can be captured in a class as a namespace:

```python
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
```

### Frontend

I chose to use a Selectbox in the Sidebar to act as page navigation.
This organizes things similarly to other Streamlit multi page examples.

The main entrypoint looks like this:

```python

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
```

Each of those `render_xyz` functions will use `st.` functions to display in the main body of the page when it is chosen in the SelectBox / drop down.

This is the `render_read` for example:

```python
def render_note(note: Note) -> None:
    """Show a note with streamlit display functions"""
    st.subheader(f"By {note.username} at {display_timestamp(note.created_timestamp)}")
    st.caption(
        f"Note #{note.rowid} -- Updated at {display_timestamp(note.updated_timestamp)}"
    )
    st.write(note.body)


def render_read(connection: sqlite3.Connection) -> None:
    """Show all of the notes in the database in a feed"""
    st.success("Reading Note Feed")
    note_rows = NoteService.list_all_notes(connection)
    with st.expander("Raw Note Table Data"):
        st.table(note_rows)

    notes = [Note(**row) for row in note_rows]
    for note in notes:
        render_note(note)
```

For more on the forms for Creating, Updating and Deleting, check out the source code on github.

### Gluing It All Together

- SQLite can run with the Python process, so we're good to deploy it wherever the Streamlit app runs
- Frontend and Backend are in one server, so there's no JSON or RPC data going between App services

Python `dataclasses.dataclass` provides a nice way of modeling simple entities like this Note example.
It lacks all of the features of `pydantic` and `attrs`, but it does have a free `__init__` with kwargs and the `dataclasses.asdict` method.

After the rows are read from the database, the data is passed into this `dataclass` Note model.
The model provides some level of validation on the data types and a Python object with known attributes for type-hinting and checking.

```python
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
```
