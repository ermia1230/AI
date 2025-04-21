#!/bin/bash
set -e

/usr/local/bin/docker-entrypoint.sh postgres &

until pg_isready -h "localhost" -p 5432 -U "$POSTGRES_USER"; do
  echo "Waiting for database to be ready..."
  sleep 2
done

echo "Creating database if not exists..."
psql -U "$POSTGRES_USER" -c "DO \$\$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'ai_project') THEN CREATE DATABASE ai_project; END IF; END \$\$;"

echo "Creating tables..."
psql -U "$POSTGRES_USER" -d ai_project -f /docker-entrypoint-initdb.d/1_0_create_table.sql

echo "Inserting data..."
source /env/bin/activate 
python3 /docker-entrypoint-initdb.d/3_0_data_migrater.py

wait $!
