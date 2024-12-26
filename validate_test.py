import psycopg2
from openai import OpenAI
import random

client = OpenAI(
    api_key="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"  # Ensure you have the API key set in your environment
)

connection = psycopg2.connect(
    host="localhost",
    port="5433",
    database="AI",
    user="postgres",
    password="xxxx"
)
cursor = connection.cursor()
fetch_query = """
SELECT review_id, review, rating, recommend 
FROM raw_data 
WHERE review IS NOT NULL
LIMIT 3;
"""
cursor.execute(fetch_query)
rows = cursor.fetchall()

for row in rows:
    review_id, review, rating, recommend = row
    print(row)
    if rating > 3:
        rating = random.randint(1, 2)  
    else:
        rating = random.randint(4, 5)
    recommend = not recommend 

    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant for validating reviews."},
            {"role": "user", "content": f"""The following is a review, along with its rating and recommendation status:
            Review: "{review}"
            Rating: {rating} (1 to 5, where 5 is excellent)
            Recommend: {recommend} (True means the user recommends the product, False means they don't)
            Please validate:
            Does the review logically match the rating and recommendation?"""}
        ]
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="gpt-4o", 
        )
        validation_result = chat_completion.choices[0].message.content.strip()
        # update_query = """
        # UPDATE raw_data
        # SET validation_result = %s
        # WHERE review_id = %s;
        # """
        # cursor.execute(update_query, (validation_result, review_id))

        print(f"Review ID: {review_id}, Validation Result: {validation_result}")
    
    except Exception as e:
        print(f"Error processing review_id {review_id}: {e}")
connection.commit()

cursor.close()
connection.close()
