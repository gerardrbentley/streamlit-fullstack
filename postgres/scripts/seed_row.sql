INSERT INTO note (rowid, username, body)
    VALUES (1, 'SYSTEM', ':beers: Auto Generated Note!!! :tada:')
ON CONFLICT
    DO NOTHING;

SELECT
    setval('note_rowid_seq', (
            SELECT
                MAX(rowid)
            FROM note));

