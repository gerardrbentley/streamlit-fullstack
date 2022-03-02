package models

import (
	"fmt"
	"net/http"
)

type Note struct {
	Rowid            int     `json:"rowid"`
	Username         string  `json:"username"`
	Body             string  `json:"body"`
	CreatedTimestamp float32 `json:"created_timestamp"`
	UpdatedTimestamp float32 `json:"updated_timestamp"`
}

type NoteList struct {
	Notes []Note `json:"notes"`
}

func (note *Note) Bind(r *http.Request) error {
	if note.Username == "" {
		return fmt.Errorf("username must be non empty")
	}
	return nil
}

func (*NoteList) Render(w http.ResponseWriter, r *http.Request) error {
	return nil
}

func (*Note) Render(w http.ResponseWriter, r *http.Request) error {
	return nil
}
