#!/bin/bash
set -e

echo "Running Database Initialization"

psql -v ON_ERROR_STOP=1 --echo-all --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
    -c "BEGIN TRANSACTION;" \
    -f /home/postgres/init_tables.sql \
    -f /home/postgres/trigger_notify.sql \
    -f /home/postgres/trigger_update_timestamp.sql \
    -f /home/postgres/apply_notify.sql \
    -f /home/postgres/apply_update_timestamp.sql \
    -f /home/postgres/seed_row.sql \
    -c "COMMIT;"
