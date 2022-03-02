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