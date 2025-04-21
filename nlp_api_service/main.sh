#!/bin/bash
set -e

DB_HOST="database"
DB_USER="postgres"
DB_PASSWORD="postgres"
DB_NAME="ai_project"

echo "Waiting for database to be ready..."
until PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c '\q' 2>/dev/null; do
    sleep 5
done
echo "Database is ready!"

if [ -f "./processed_data.sql" ]; then
    echo "Found processed_data.sql. Proceeding with data deletion and import..."
    EXISTING_TABLES=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")

    if [ "$EXISTING_TABLES" -gt 0 ]; then
        echo "Tables found. Dropping all tables..."
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP SCHEMA public CASCADE;"
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "CREATE SCHEMA public;"
    fi

    echo "Importing processed_data.sql into the database..."
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f ./processed_data.sql
else
    echo "No processed_data.sql found. Running NLP service to mine data and store into the database ..."
    source /env/bin/activate
    python3 nlp_service.py
fi