CREATE TABLE IF NOT EXISTS note (
    rowid serial NOT NULL PRIMARY KEY,
    created_timestamp timestamptz NOT NULL DEFAULT NOW(),
    updated_timestamp timestamptz NOT NULL DEFAULT NOW(),
    username varchar(140) NOT NULL,
    body varchar(140) NOT NULL
);

