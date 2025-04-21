import psycopg2
from openai import OpenAI
import csv
import json
from dotenv import load_dotenv
import os

FETCH_QUERIES = {
    "pants": """
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
                  AND rating < 4
                LIMIT 10; 
            """,
    "jackets": """
                WITH FilteredClothing AS (
                    SELECT clothing_id
                    FROM raw_data
                    WHERE class_name = 'Jackets'
                    GROUP BY clothing_id
                    HAVING COUNT(review_id) >= 50
                )
                SELECT clothing_id, review_id, review, rating, recommend
                FROM raw_data
                WHERE clothing_id IN (SELECT clothing_id FROM FilteredClothing)
                  AND review IS NOT NULL
                  AND rating < 4
                LIMIT 10;
            """,
    "jeans": """
                WITH FilteredClothing AS (
                    SELECT clothing_id
                    FROM raw_data
                    WHERE class_name = 'Jeans'
                    GROUP BY clothing_id
                    HAVING COUNT(review_id) >= 50
                )
                SELECT clothing_id, review_id, review, rating, recommend
                FROM raw_data
                WHERE clothing_id IN (SELECT clothing_id FROM FilteredClothing)
                  AND review IS NOT NULL
                  AND rating < 4
                LIMIT 10;
            """
}


def init():
    load_dotenv("./local.env")


def create_insert_query(name_of_table):
    return f"""
        INSERT INTO {name_of_table} ( clothing_id ,review_id, review, rating, recommend, validation_result, problem_category)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        
        
def create_table_query(name_of_table):
    return f"""
        CREATE TABLE IF NOT EXISTS {name_of_table} (
        id SERIAL PRIMARY KEY,
        clothing_id INTEGER,
        review_id INTEGER,
        review TEXT,
        rating INTEGER,
        recommend BOOLEAN,
        validation_result BOOLEAN,
        problem_category TEXT
    );"""
    
    
def get_connection():
    return psycopg2.connect(
    host=os.getenv("DB_HOST", "database"),
    port=os.getenv("DB_PORT", 5432),
    database=os.getenv("DB_DATABASE", "ai_project"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD","postgres")
)
    
    
def get_openai_api():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def sementisize_review(query_key, table_name):
    client = get_openai_api()
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(FETCH_QUERIES[query_key])
    rows = cursor.fetchall()
    row_num = len(rows)
    create_validate_pants_table = create_table_query(table_name)
    cursor.execute(create_validate_pants_table)
    insert_validate_pants_query = create_insert_query(table_name)
    counter = 1
    for row in rows:
        clothing_id, review_id, review, rating, recommend = row
        try:
            messages = [{
            "role": "system",
            "content": """You are a data analyst that validates and classifies reviews for a clothing product.

        Use this thinking process for each input:

        1. Analyze the review text for its sentiment and specific problem mentions.
        2. Compare it to the rating:
           - If a high rating (4 or 5) is paired with mostly negative feedback, mark validation as false.
           - If a low rating (1 or 2) is paired with mostly positive feedback, mark validation as false.
           - If the review sentiment and rating match, mark validation as true.
        3. If validation is true, extract problem categories that clearly apply from the list.
        4. If validation is false, set problemCategory to an empty array.

        Problem Categories:
        ['Inconsistent Sizing', 'Poor Quality and Durability', 'Fabric Issues', 'Fit and Design Flaws', 'Misleading Product Representations', 'Functional and Practical Limitations', 'Long Wait Times and Delivery Issues']

        ### Example 1:
        Review: 'The shirt's material feels very cheap, and it tore after just one wash.'
        Rating: '1'
        Recommend: 'False'

        Output:
        {"validation": "true", "problemCategory": ["Poor Quality and Durability", "Fabric Issues"]}

        ### Example 2:
        Review: 'I love the design, but it doesn't match the color shown online.'
        Rating: '5'
        Recommend: 'True'

        Output:
        {"validation": "false", "problemCategory": []}

        When you are done thinking, output only the JSON object and nothing else.
        Now apply the same reasoning to the following input."""
        },
        {
            "role": "user",
            "content": f"""Review: '''{review}'''
        Rating: '''{rating}'''
        Recommend: '''{recommend}'''
        Problem Categories: '''
        Inconsistent Sizing, Poor Quality and Durability, Fabric Issues, Fit and Design Flaws, Misleading Product Representations, Functional and Practical Limitations, Long Wait Times and Delivery Issues'''."""
        }
        ]
            chat_completion = client.chat.completions.create(
                messages=messages,
                model="gpt-4",
                temperature=0.0,
            )
            validation_result = chat_completion.choices[0].message.content
            try:
                validation_result = validation_result.strip("```").strip()
                validation_result_json = json.loads(validation_result)
                validation = validation_result_json["validation"]
                problem_category_array = validation_result_json["problemCategory"]
                validation = validation == "true"
                if validation and not problem_category_array:
                    problem_category = "Others"
                elif not validation and not problem_category_array:
                    problem_category = "Invalid"
                else:
                    problem_category = problem_category_array[0]
            except ValueError:
                print(f"Unexpected GPT response format: {validation_result}")
                continue
            cursor.execute(insert_validate_pants_query, (clothing_id, review_id, review, rating, recommend, validation, problem_category))
            print(f"ReviewID: {review_id} - ({counter} / {row_num}) has been processed for category: {query_key}. | RESULT: {problem_category}")
            counter += 1    
        except Exception as e:
            print(f"Error processing review_id {review_id}: {e}")
    connection.commit()
    cursor.close()
    connection.close()
    
    
def main():
    init()
    sementisize_review("pants", "validated_reviews_pants")
    sementisize_review("jackets", "validated_reviews_jacket")
    sementisize_review("jeans", "validated_reviews_jeans")
    
    
if __name__ == "__main__":
    main()    
