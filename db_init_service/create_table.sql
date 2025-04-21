\c ai_project

CREATE TABLE IF NOT EXISTS raw_data (
    Review_id SERIAL PRIMARY KEY,  
    clothing_id INT NOT NULL, 
    age INT NOT NULL,  
    title VARCHAR(200),
    review VARCHAR(4000),           
    rating INT NOT NULL, 
    recommend BOOLEAN NOT NULL, 
    positive_feedback_count INT,
    division VARCHAR(30),
    department VARCHAR(30),
    class_name VARCHAR(30)
);
