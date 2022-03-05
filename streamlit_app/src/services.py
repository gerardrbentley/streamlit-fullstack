from dataclasses import asdict
import os
from typing import List
import logging

import httpx

from src.models import Note
from src.models import Note, BaseNote

BACKEND_HOST = os.getenv("BACKEND_HOST", "backend")
BACKEND_PORT = os.getenv("BACKEND_PORT", "3000")

CHAR_LIMIT = 140

class NoteService:
    """Namespace for Database Related Note Operations"""

    @staticmethod
    def list_all_notes() -> List[Note]:
        response = httpx.get(f"http://{BACKEND_HOST}:{BACKEND_PORT}/notes")
        logging.info(response)
        json_notes = response.json()
        notes = [Note(**note) for note in json_notes["notes"]]
        return notes

    @staticmethod
    def create_note(note: BaseNote) -> None:
        """Create a Note in the database"""
        response = httpx.post(
            f"http://{BACKEND_HOST}:{BACKEND_PORT}/notes", json=asdict(note)
        )
        return response

    @staticmethod
    def update_note(note: Note) -> None:
        """Replace a Note in the database"""
        response = httpx.put(
            f"http://{BACKEND_HOST}:{BACKEND_PORT}/notes/{note.rowid}",
            json=asdict(note),
        )
        return response

    @staticmethod
    def delete_note(note: Note) -> None:
        """Delete a Note in the database"""
        # DELETE spec doesn't include json body: https://github.com/encode/httpx/discussions/1587
        response = httpx.request(
            method="delete",
            url=f"http://{BACKEND_HOST}:{BACKEND_PORT}/notes/{note.rowid}",
            json=asdict(note),
        )
        return response
