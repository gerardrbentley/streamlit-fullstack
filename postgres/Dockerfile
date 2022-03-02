FROM postgres:14.2

COPY init-user-db.sh /docker-entrypoint-initdb.d/init-user-db.sh
COPY ./scripts /home/postgres
