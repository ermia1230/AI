import psycopg2
import csv 
from dotenv import load_dotenv
import os



def init():
    load_dotenv("./local.env")


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432),
        database=os.getenv("DB_DATABASE", "ai_project"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD","postgres")
    )


def migrate_csv_to_postgres():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("TRUNCATE TABLE raw_data RESTART IDENTITY;")
    with open('2_0_data.csv', mode='r', newline='') as file:
        reader = csv.reader(file, delimiter=';')
        count = 0
        for row in reader:
            if count == 0:
                print("LAUNCHING DATA MIGRATION ...")
            else:
                clothing_id = int(row[1]) if row[1] else None
                age = int(row[2]) if row[2] else None
                title = row[3] if row[3] else None
                review = row[4] if row[4] and row[4].strip() != "" else None
                rating = int(row[5]) if row[5] else None
                recommend = True if int(row[6]) == 1 else False
                positive_feedback_count = int(row[7]) if row[7] else None
                division = row[8] if row[8] else None
                department = row[9] if row[9] else None
                class_name = row[10] if row[10] else None
                insert_query = """
                INSERT INTO raw_data (clothing_id, age, title, review, rating, recommend, positive_feedback_count, division, department, class_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_query, (clothing_id, age, title, review, rating, recommend, positive_feedback_count, division, department, class_name))
            count += 1
        print(f"Total rows processed: {count - 1}")
    connection.commit()
    cursor.close()
    connection.close()


def main():
    init()
    migrate_csv_to_postgres()
    

if __name__ == "__main__":
    main()  
