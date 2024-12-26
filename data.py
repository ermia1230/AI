import psycopg2
import csv 

connection = psycopg2.connect(
    host="localhost",    
    port="5433",         
    database="AI",       
    user="postgres",     
    password="xxxx"
)

cursor = connection.cursor()
cursor.execute("TRUNCATE TABLE raw_data RESTART IDENTITY;")
with open('data.csv', mode='r', newline='') as file:
    reader = csv.reader(file, delimiter=';')
    count = 0
    for row in reader:
        if count == 0:
            print("Hej")
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
