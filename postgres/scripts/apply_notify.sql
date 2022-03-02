CREATE TRIGGER notify_on_message_insert
    AFTER INSERT ON note
    FOR EACH ROW
    EXECUTE PROCEDURE notify_on_insert ();

