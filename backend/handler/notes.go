package handler

import (
	"context"
	"fmt"
	"fullstack/backend/db"
	"fullstack/backend/models"
	"log"
	"net/http"
	"strconv"

	"github.com/go-chi/chi"
	"github.com/go-chi/render"
)

type NoteKey struct {
	key string
}

var noteIdKey = NoteKey{key: "note-key"}

func notes(router chi.Router) {
	router.Get("/", getAllNotes)
	router.Post("/", createNote)
	router.Route("/{noteId}", func(router chi.Router) {
		router.Use(NoteContext)
		router.Get("/", getNote)
		router.Put("/", updateNote)
		router.Delete("/", deleteNote)
	})
}

func NoteContext(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		noteId := chi.URLParam(r, "noteId")
		if noteId == "" {
			render.Render(w, r, ErrorRenderer(fmt.Errorf("note ID is required")))
			return
		}
		id, err := strconv.Atoi(noteId)
		if err != nil {
			render.Render(w, r, ErrorRenderer(fmt.Errorf("invalid Note ID")))
			return
		}
		ctx := context.WithValue(r.Context(), noteIdKey, id)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

func createNote(w http.ResponseWriter, r *http.Request) {
	log.Printf("Create: %v", r)
	note := &models.Note{}
	if err := render.Bind(r, note); err != nil {
		render.Render(w, r, ErrBadRequest)
		return
	}
	if err := dbInstance.AddNote(note); err != nil {
		render.Render(w, r, ErrorRenderer(err))
		return
	}
	if err := render.Render(w, r, note); err != nil {
		render.Render(w, r, ServerErrorRenderer(err))
		return
	}
}

func getAllNotes(w http.ResponseWriter, r *http.Request) {
	notes, err := dbInstance.GetAllNotes()
	if err != nil {
		log.Printf("Error: %s", err.Error())
		render.Render(w, r, ServerErrorRenderer(err))
		return
	}
	if err := render.Render(w, r, notes); err != nil {
		render.Render(w, r, ErrorRenderer(err))
	}
}

func getNote(w http.ResponseWriter, r *http.Request) {
	noteId := r.Context().Value(noteIdKey).(int)
	note, err := dbInstance.GetNoteById(noteId)
	if err != nil {
		if err == db.ErrRowNotFound {
			render.Render(w, r, ErrNotFound)
		} else {
			render.Render(w, r, ErrorRenderer(err))
		}
		return
	}
	if err := render.Render(w, r, &note); err != nil {
		render.Render(w, r, ServerErrorRenderer(err))
		return
	}
}

func deleteNote(w http.ResponseWriter, r *http.Request) {
	noteId := r.Context().Value(noteIdKey).(int)
	err := dbInstance.DeleteNote(noteId)
	if err != nil {
		if err == db.ErrRowNotFound {
			render.Render(w, r, ErrNotFound)
		} else {
			render.Render(w, r, ServerErrorRenderer(err))
		}
		return
	}
}

func updateNote(w http.ResponseWriter, r *http.Request) {
	log.Printf("Update %v", r)
	noteId := r.Context().Value(noteIdKey).(int)
	noteData := models.Note{}
	if err := render.Bind(r, &noteData); err != nil {
		render.Render(w, r, ErrBadRequest)
		return
	}
	item, err := dbInstance.UpdateNote(noteId, noteData)
	if err != nil {
		if err == db.ErrRowNotFound {
			render.Render(w, r, ErrNotFound)
		} else {
			render.Render(w, r, ServerErrorRenderer(err))
		}
		return
	}
	if err := render.Render(w, r, &item); err != nil {
		render.Render(w, r, ServerErrorRenderer(err))
		return
	}
}
