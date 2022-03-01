package db

import (
	"fullstack/backend/models"
)

func (db Database) GetAllNotes() (*models.NoteList, error) {
	list := &models.NoteList{}
	rows, err := db.Connection.Query("SELECT rowid, created_timestamp, updated_timestamp, username, body FROM notes ORDER BY rowid DESC;")

	if err != nil {
		return list, err
	}

	for rows.Next() {
		var note models.Note
		err := rows.Scan(&note.Rowid, &note.CreatedTimestamp, &note.UpdatedTimestamp, &note.Username, &note.Body)

		if err != nil {
			return list, err
		}
		list.Notes = append(list.Notes, note)
	}

	return list, nil
}
