FROM python:3.12
RUN apt-get update && apt-get install -y \
    libpq-dev \
    postgresql-client \
    python3-venv \
    && rm -rf /var/lib/apt/lists/* && \
    python3 -m venv /env && \
    /env/bin/pip install --no-cache-dir pandas psycopg2-binary python-dotenv openai psycopg2
WORKDIR /app
COPY . /app/
RUN chmod +x main.sh
ENTRYPOINT ["./main.sh"]
