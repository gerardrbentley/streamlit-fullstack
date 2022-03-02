package db

import (
	"database/sql"
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

func (db Database) GetNoteById(noteId int) (models.Note, error) {
	note := models.Note{}
	query := `SELECT rowid, created_timestamp, updated_timestamp, username, body FROM notes WHERE rowid = $1;`
	row := db.Connection.QueryRow(query, noteId)
	err := row.Scan(&note.Rowid, &note.CreatedTimestamp, &note.UpdatedTimestamp, &note.Username, &note.Body)

	if err == sql.ErrNoRows {
		return note, ErrNoMatch
	} else {
		log.Printf("%+v\n", note)
		return note, err
	}
}

func (db Database) AddNote(note *models.Note) error {
	var id int
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

func (db Database) UpdateNote(noteId int, noteData models.Note) (models.Note, error) {
	log.Printf("%v, %v", noteId, noteData)
	note := models.Note{}
	query := `UPDATE notes SET updated_timestamp=$1, username=$2, body=$3 WHERE rowid=$4 RETURNING rowid, username, body, created_timestamp, updated_timestamp;`
	row := db.Connection.QueryRow(query, noteData.UpdatedTimestamp, noteData.Username, noteData.Body, noteId)
	err := row.Scan(&note.Rowid, &note.Username, &note.Body, &note.CreatedTimestamp, &note.UpdatedTimestamp)
	if err != nil {
		if err == sql.ErrNoRows {
			return note, ErrNoMatch
		}
		return note, err
	}
	log.Printf("%+v\n", note)
	return note, nil
}

func (db Database) DeleteNote(noteId int) error {
	query := `DELETE FROM notes WHERE rowid = $1;`
	_, err := db.Connection.Exec(query, noteId)
	if err == sql.ErrNoRows {
		return ErrNoMatch
	} else {
		return err
	}
}
