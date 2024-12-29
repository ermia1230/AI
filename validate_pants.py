import psycopg2
from openai import OpenAI
import csv

client = OpenAI(
    api_key="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"
)

connection = psycopg2.connect(
    host="localhost",
    port="5433",
    database="AI",
    user="postgres",
    password="xxx"
)
cursor = connection.cursor()

fetch_query = """
WITH FilteredClothing AS (
    SELECT clothing_id
    FROM raw_data
    WHERE class_name = 'Pants'
    GROUP BY clothing_id
    HAVING COUNT(review_id) >= 50
)
SELECT clothing_id, review_id, review, rating, recommend
FROM raw_data
WHERE clothing_id IN (SELECT clothing_id FROM FilteredClothing)
  AND review IS NOT NULL
  AND rating < 4;
"""
cursor.execute(fetch_query)
rows = cursor.fetchall()

create_table_query = """
CREATE TABLE IF NOT EXISTS validated_reviews_pants (
    id SERIAL PRIMARY KEY,
    clothing_id INTEGER,
    review_id INTEGER,
    review TEXT,
    rating INTEGER,
    recommend BOOLEAN,
    validation_result BOOLEAN,
    problem_category INTEGER
);
"""
cursor.execute(create_table_query)

with open('validated_reviews_pants.csv', mode='w', newline='', encoding='utf-8') as file:
    csv_writer = csv.writer(file, delimiter=',')
    csv_writer.writerow(["clothing_id", "review", "rating", "recommend", "validation_result", "problem_category"])

    for row in rows:
        clothing_id, review_id, review, rating, recommend = row
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant for validating reviews."},
                {"role": "user", "content": f"""The following is a review, along with its rating, recommendation status, and identified problem category:
                Review: \"{review}\"
                Rating: {rating} (1 to 5, where 5 is excellent)
                Recommend: {recommend} (True means the user recommends the product, False means they don't)
                Problem Category: (Choose from the following categories:
                1- Inconsistent Sizing
                2- Poor Quality and Durability
                3- Fabric Issues
                4- Fit and Design Flaws
                5- Misleading Product Representations
                6- Functional and Practical Limitations
                7- Long Wait Times and Delivery Issues
                8- Others)
                Please validate:
                Does the review logically match the rating, recommendation, and identified problem category? Respond with 'True' or 'False', followed by the problem category number."""}
            ]

            chat_completion = client.chat.completions.create(
                messages=messages,
                model="gpt-4o",
                max_tokens=4
            )
            validation_result = chat_completion.choices[0].message.content.strip()
            try:
                validation, problem_category = validation_result.split(", ")
                validation = validation == "True"
                problem_category = int(problem_category) 
            except ValueError:
                print(f"Unexpected GPT response format: {validation_result}")
                continue
            insert_query = """
            INSERT INTO validated_reviews_pants ( clothing_id ,review_id, review, rating, recommend, validation_result, problem_category)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(insert_query, (clothing_id, review_id, review, rating, recommend, validation, problem_category))
            csv_writer.writerow([clothing_id, review, rating, recommend, validation, problem_category])
            print(f"Inserted review_id {review_id} with validation_result {validation} and problem_category {problem_category}")
        except Exception as e:
            print(f"Error processing review_id {review_id}: {e}")

connection.commit()
cursor.close()
connection.close()
