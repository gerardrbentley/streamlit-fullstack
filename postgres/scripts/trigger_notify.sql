CREATE OR REPLACE FUNCTION notify_on_insert ()
    RETURNS TRIGGER
    AS $$
BEGIN
    PERFORM
        pg_notify('channel_note', CAST(row_to_json(NEW) AS text));
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;

