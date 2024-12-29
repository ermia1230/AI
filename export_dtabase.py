import subprocess

host = "localhost"
port = "5433"
database = "AI"
user = "postgres"
password = "xxxx"
output_file = "AI_backup.sql"

command = [
    "pg_dump",
    f"--host={host}",
    f"--port={port}",
    f"--username={user}",
    f"--dbname={database}",
    "--no-password",
    "--file", output_file
]

try:
    result = subprocess.run(command, env={"PGPASSWORD": password}, check=True, text=True)
    print(f"Backup successful. File saved as: {output_file}")
except subprocess.CalledProcessError as e:
    print(f"Error during backup: {e}")
