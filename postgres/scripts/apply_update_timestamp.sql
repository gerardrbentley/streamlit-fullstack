CREATE TRIGGER set_timestamp
    BEFORE UPDATE ON note
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_set_timestamp ();

