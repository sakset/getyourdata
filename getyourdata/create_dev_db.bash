#!/bin/bash

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

execute_psql () {
    psql -e -c "$1"
    if [[ $? -ne 0 ]]; then
        echo "Error executing command: $1"
        exit 1
    fi
}

setup_dev_db () {
    # Dropping old database and user
    execute_psql "DROP DATABASE IF EXISTS $1devdb" &&
    execute_psql "DROP DATABASE IF EXISTS test_$1devdb" &&
    execute_psql "DROP USER IF EXISTS $1devuser" &&
    # Creating new database and user
    execute_psql "CREATE DATABASE $1devdb" &&
    execute_psql "CREATE USER $1devuser WITH PASSWORD '$1devpwd'" &&
    execute_psql "ALTER USER $1devuser CREATEDB" &&
    execute_psql "ALTER ROLE $1devuser SET client_encoding TO 'utf8'" &&
    execute_psql "ALTER ROLE $1devuser SET default_transaction_isolation TO 'read committed'" &&
    execute_psql "ALTER ROLE $1devuser SET timezone TO 'UTC'" &&
    execute_psql "GRANT ALL PRIVILEGES ON DATABASE $1devdb TO $1devuser" &&
    echo "Database '$1devdb' created with user '$1devuser' and password '$1devpwd'"
}

cd "/tmp" || echo "/tmp not found..."
export -f execute_psql
export -f setup_dev_db

if [[ $# -eq 0 ]]; then
    su postgres -c "setup_dev_db getyourdata"
else
    su postgres -c "setup_dev_db $1"
fi
