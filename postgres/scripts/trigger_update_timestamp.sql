CREATE OR REPLACE FUNCTION trigger_set_timestamp ()
    RETURNS TRIGGER
    AS $$
BEGIN
    NEW.updated_timestamp = NOW();
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;

