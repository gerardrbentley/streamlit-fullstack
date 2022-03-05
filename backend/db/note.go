package db

import (
	"database/sql"
	"fullstack/backend/models"
	"log"
)

func (db Database) GetAllNotes() (*models.NoteList, error) {
	notes := &models.NoteList{}
	query := `SELECT rowid, date_part('epoch', created_timestamp), date_part('epoch', updated_timestamp), 
		username, body FROM note ORDER BY rowid DESC;`
	log.Println("Getting All Notes")
	rows, err := db.Connection.Query(query)

	if err != nil {
		return notes, err
	}

	for rows.Next() {
		var note models.Note
		err := rows.Scan(&note.Rowid, &note.CreatedTimestamp, &note.UpdatedTimestamp, &note.Username, &note.Body)

		if err != nil {
			log.Println("Error Scanning Row", err)
			return notes, err
		}

		notes.Notes = append(notes.Notes, note)
	}
	log.Println("Returning ", len(notes.Notes), " Rows")
	return notes, nil
}

func (db Database) GetNoteById(noteId int) (models.Note, error) {
	note := models.Note{}
	query := `SELECT rowid, date_part('epoch', created_timestamp), date_part('epoch', updated_timestamp), 
		username, body FROM note WHERE rowid = $1;`
	log.Println("Getting Note with ID: ", noteId)
	row := db.Connection.QueryRow(query, noteId)
	err := row.Scan(&note.Rowid, &note.CreatedTimestamp, &note.UpdatedTimestamp, &note.Username, &note.Body)

	if err == sql.ErrNoRows {
		log.Println("No Rows Found ", err)
		return note, ErrRowNotFound
	} else {
		log.Println("Returning ", note)
		return note, err
	}
}

func (db Database) AddNote(note *models.Note) error {
	var id int
	query := `INSERT into note(username, body)
    	VALUES($1, $2) RETURNING rowid;`
	log.Println("Adding New Note", note)
	rows := db.Connection.QueryRow(query, note.Username, note.Body)
	err := rows.Scan(&id)
	if err != nil {
		log.Println("Couldn't Add Note", err)
		return err
	}
	note.Rowid = id
	log.Printf("Returning ", note)
	return nil
}

func (db Database) UpdateNote(noteId int, noteData models.Note) (models.Note, error) {
	note := models.Note{}
	query := `UPDATE note SET username=$1, body=$2 WHERE rowid=$3 
		RETURNING rowid, username, body, date_part('epoch', created_timestamp), date_part('epoch', updated_timestamp);`
	log.Println("Updating Note with ID ", noteId, ". Setting Fields ", noteData)
	row := db.Connection.QueryRow(query, noteData.Username, noteData.Body, noteId)
	err := row.Scan(&note.Rowid, &note.Username, &note.Body, &note.CreatedTimestamp, &note.UpdatedTimestamp)
	if err != nil {
		if err == sql.ErrNoRows {
			log.Println("Note Not Updated ", err)
			return note, ErrRowNotFound
		}
		log.Println("Error Scanning Result ", err)
		return note, err
	}
	log.Println(note)
	return note, nil
}

func (db Database) DeleteNote(noteId int) error {
	query := `DELETE FROM note WHERE rowid = $1 RETURNING rowid;`
	log.Println("Deleting Note with ID ", noteId)
	_, err := db.Connection.Exec(query, noteId)
	if err == sql.ErrNoRows {
		log.Println("Note not Deleted ", err)
		return ErrRowNotFound
	} else {
		return err
	}
}
