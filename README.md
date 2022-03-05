# Streamlit Full Stack App

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/gerardrbentley/streamlit-fullstack/app.py)

- Postgres Version Live at [streamlit-postgres.gerardbentley.com](https://streamlit-postgres.gerardbentley.com)

Demo Repo on building a Full Stack CRUD App with Streamlit with multiple levels of complexity.

Create, Read, Update, and Delete from a feed of 140 character markdown notes.

Run a single Streamlit server with SQLite Database, a Streamlit + Postgres + Nginx Docker-Compose stack, or a full Streamlit + Go + Postgres + Nginx stack

- :mouse: littlest (original) version wil remain on [branch `littlest`](https://github.com/gerardrbentley/streamlit-fullstack/tree/littlest)
- :elephant: Postgres (`psycopg3`) + Nginx + Docker-Compose version at [branch `psycopg`](https://github.com/gerardrbentley/streamlit-fullstack/tree/psycopg) and Live at [streamlit-postgres.gerardbentley.com](https://streamlit-postgres.gerardbentley.com)
- Go REST API + Postgres + Nginx + Docker-Compose version at [branch `go`](https://github.com/gerardrbentley/streamlit-fullstack/tree/go)

## Run Streamlit + Go + Postgres + Nginx Version

For when that SQLite database crumbles and Backend needs get complex.

```sh
curl https://github.com/gerardrbentley/streamlit-fullstack/archive/refs/heads/go.zip -O -L
unzip go
cd streamlit-fullstack-go
cp example.env .env.dev
# Production: Fill out .env with real credentials, docker compose should shut off streamlit ports
cp streamlit_app/.streamlit/config.example.toml streamlit_app/.streamlit/config.toml
# Production: random cookie secret
# python -c "from pathlib import Path; from string import ascii_lowercase, digits; from random import choice; Path('streamlit_app/.streamlit/config.toml').write_text(Path('streamlit_app/.streamlit/config.example.toml').read_text().replace('changemecookiesecret', ''.join([choice(ascii_lowercase + digits) for _ in range(64)])))"
docker-compose up
# Will take some time to download all layers and dependencies
```

*NOTE:* Any changes to Go server require a new build of that container and restart. (or just kill the compose stack and `up --build` for the lazy)

Go backend server relies on [go-chi](https://go-chi.io/#/) as the routing layer.

Database connection relies on [lib/pq](https://github.com/lib/pq) to communicate with postgres.

## Run Streamlit + Postgres + Nginx Version

Ran with `Docker version 20.10.12`, `Docker Compose version v2.2.3`:

```sh
curl https://github.com/gerardrbentley/streamlit-fullstack/archive/refs/heads/psycopg.zip -O -L
unzip psycopg
cd streamlit-fullstack-psycopg
cp example.env .env.dev
# Production: Fill out .env with real credentials, docker compose should shut off streamlit ports
cp streamlit_app/.streamlit/config.example.toml streamlit_app/.streamlit/config.toml
# Production: random cookie secret
# python -c "from pathlib import Path; from string import ascii_lowercase, digits; from random import choice; Path('streamlit_app/.streamlit/config.toml').write_text(Path('streamlit_app/.streamlit/config.example.toml').read_text().replace('changemecookiesecret', ''.join([choice(ascii_lowercase + digits) for _ in range(64)])))"
docker-compose up
# Will take some time to download all layers and python requirements
```

*Notes:* 

- Use `--build` with docker-compose to rebuild image after changing dependencies / dockerfile.
- Use `-d` with docker-compose to detach from terminal output (remember to `docker-compose down` when you want it to stop)
- Use `docker-compose down --volumes` to wipe database (docker volume)

## Run Streamlit w/ SQLite Version

```sh
curl https://raw.githubusercontent.com/gerardrbentley/streamlit-fullstack/littlest/app.py -O
pip install streamlit
streamlit run app.py
```

(Don't have Python / `pip` installed? [here's my way](https://tech.gerardbentley.com/python/beginner/2022/01/29/install-python.html))

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

#### Postgres

The Postgres server in dev and when used in docker-compose stack is dockerized.

It spins up as a service that supports the streamlit app.
The Streamlit startup sequence naively createst the notes table if it doesn't exist, and trys to seed a row.
(This action is also cached by Streamlit, so itsn't terrible, but definitely not [12 factor app](https://12factor.net/admin-processes) standard for admin process)

This version uses synchronous `psycopg` v3 to read and write similarly to the SQLite statements, with the bonus of reading rows directly from the database into our `dataclass` Note model.

A `pydantic.BaseSettings` object grabs the postgres connection variables from environment, which are provided by docker-compose (*note* EXPORT env variables if you have your own postgres server) 

```python

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
```


#### SQLite (littlest version)

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

#### Psycopg

Version 3 of `psycopg` has some static typing benefits built in.
Here we had a function that executes a query then returns all the matching / fetched rows.

The nice thing is if we pass a dataclass type as the `dclass` arg we'll get out a list of that type!

We also have to fix the execute query function that doesn't return any rows, as psycopg will raise an Exception.

```python
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
```

#### SQLite

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

#### Updated

The main `app.py` entrypoint now contains less code, having been split into `db.py`, `data.py`, `views.py`, and `formatting.py`.

It now focuses on the setup, connecting to the database, and rendering the selected page view

```python
import src.views as views
from src.db import PsycopgSettings, create_notes_table, seed_notes_table

PAGES = {
    "Read Note Feed": views.render_read,  # Read first for display default
    "Create a Note": views.render_create,
    "Update a Note": views.render_update,
    "Delete a Note": views.render_delete,
    "About": views.render_about,
}

def main() -> None:
    """Main Streamlit App Entry"""
    connection_args = PsycopgSettings().get_connection_args()
    connection = get_connection(**connection_args)
    init_db(connection)

    st.header(f"The Littlest Fullstack App + Postgres :elephant:!")
    render_sidebar(connection)


def render_sidebar(connection: psycopg.Connection) -> None:
    """Provides Selectbox Drop Down for which view to render"""
    choice = st.sidebar.radio("Go To Page:", PAGES.keys())
    render_func = PAGES.get(choice)
    render_func(connection)
```

#### Littlest

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
