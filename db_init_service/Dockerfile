FROM postgres:latest

RUN apt-get update && apt-get install -y \
    libpq-dev \
    python3.12 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv /env

RUN /env/bin/pip install --no-cache-dir pandas psycopg2-binary python-dotenv psycopg2 
WORKDIR /docker-entrypoint-initdb.d

COPY ./main.sh /entrypoint.sh
COPY ./create_table.sql ./1_0_create_table.sql
COPY ./data.csv ./2_0_data.csv
COPY ./data_migrater.py ./3_0_data_migrater.py
COPY ./local.env ./local.env

RUN chmod +x /entrypoint.sh


ENTRYPOINT ["/entrypoint.sh"]
