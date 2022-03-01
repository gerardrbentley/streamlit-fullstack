package db

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/lib/pq"
)

const (
	HOST = "db"
	PORT = 5432
)

// Request a row that doesn't exist
var ErrNoMatch = fmt.Errorf("no matching record")

type Database struct {
	Connection *sql.DB
}

func Initialize(username, password, database string) (Database, error) {
	db := Database{}
	connectionString := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
		HOST, PORT, username, password, database)
	conn, err := sql.Open("postgres", connectionString)

	if err != nil {
		return db, err
	}
	db.Connection = conn
	err = db.Connection.Ping()

	if err != nil {
		return db, err
	}

	log.Println("Database connection established")
	return db, nil

}
