package handler

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"strconv"

	"github.com/go-chi/chi"
	"github.com/go-chi/render"
)

type NoteKey struct {
	key string
}

var noteIDKey = NoteKey{key: "note-key"}

func notes(router chi.Router) {
	router.Get("/", getAllNotes)
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
		}
		ctx := context.WithValue(r.Context(), noteIDKey, id)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
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
