package db

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/lib/pq"
)

var ErrRowNotFound = fmt.Errorf("no matching record")

type Database struct {
	Connection *sql.DB
}

type PGConnection struct {
	User     string
	Password string
	DbName   string
	Host     string
	Port     int
}

func Initialize(pg PGConnection) (Database, error) {
	db := Database{}
	connectionString := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
		pg.Host, pg.Port, pg.User, pg.Password, pg.DbName)
	log.Println("Attempting to connect to postgres")
	connection, err := sql.Open("postgres", connectionString)

	if err != nil {
		return db, err
	}

	db.Connection = connection
	err = db.Connection.Ping()

	if err != nil {
		return db, err
	}

	log.Println("Database connection established")
	return db, nil

}
