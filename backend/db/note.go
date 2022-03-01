package db

import (
	"fullstack/backend/models"
	"log"
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

func (db Database) AddNote(note *models.Note) error {
	var id int
	// timestamp := now.Unix()
	query := `INSERT into notes(username, body, created_timestamp, updated_timestamp)
    VALUES($1, $2, $3, $4) RETURNING rowid;`
	rows := db.Connection.QueryRow(query, note.Username, note.Body, note.CreatedTimestamp, note.UpdatedTimestamp)
	err := rows.Scan(&id)
	if err != nil {
		return err
	}
	note.Rowid = id
	log.Printf("%+v\n", note)
	return nil
}
