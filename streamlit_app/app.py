import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

import streamlit as st

import src.views as views

PAGES = {
    "Read Note Feed": views.render_read,  # Read first for display default
    "Create a Note": views.render_create,
    "Update a Note": views.render_update,
    "Delete a Note": views.render_delete,
    "About": views.render_about,
}

def main() -> None:
    """Main Streamlit App Entry"""
    st.header(f"The Littlest Fullstack App + Postgres + Go!")
    render_sidebar()


def render_sidebar() -> None:
    """Provides Selectbox Drop Down for which view to render"""
    choice = st.sidebar.radio("Go To Page:", PAGES.keys())
    render_func = PAGES.get(choice)
    render_func()


if __name__ == "__main__":
    main()
