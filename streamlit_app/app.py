from time import time
import psycopg
import os

import streamlit as st

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
    max_retries = 5
    with st.spinner("Get Connection"):
        for retry_num in range(max_retries):
            try:
                connection = get_connection(**connection_args)
                break
            except psycopg.OperationalError as e:
                time.sleep(2 * retry_num + 2)
            except Exception as e:
                raise e

    init_db(connection)

    st.header(f"The Littlest Fullstack App + Postgres :elephant:!")
    render_sidebar(connection)


def render_sidebar(connection: psycopg.Connection) -> None:
    """Provides Selectbox Drop Down for which view to render"""
    choice = st.sidebar.radio("Go To Page:", PAGES.keys())
    render_func = PAGES.get(choice)
    render_func(connection)


@st.cache(hash_funcs={psycopg.Connection: id}, suppress_st_warning=True)
def get_connection(**kwargs) -> psycopg.Connection:
    """Make a connection object to psycopg
    Threading in Streamlit / Python with db Connection:
    - https://discuss.streamlit.io/t/prediction-analysis-and-creating-a-database/3504/2
    Postgres connection args:
    - https://www.postgresql.org/docs/9.1/libpq-connect.html
    """
    connection = psycopg.connect(**kwargs, autocommit=True)
    return connection


@st.cache(hash_funcs={psycopg.Connection: id}, suppress_st_warning=True)
def init_db(connection: psycopg.Connection) -> None:
    """Create table and seed data as needed"""
    st.warning("Init DB")
    create_notes_table(connection)
    seed_notes_table(connection)



if __name__ == "__main__":
    main()
