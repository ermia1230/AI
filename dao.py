import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os

class DAO:
    def __init__(self, fetch_query):
        self._problem_category_map = {
            1: 'Inconsistent Sizing',
            2: 'Poor Quality and Durability',
            3: 'Fabric Issues',
            4: 'Fit and Design Flaws',
            5: 'Misleading Product Representations',
            6: 'Functional and Practical Limitations',
            7: 'Long Wait Times and Delivery Issues',
            8: 'Others'
        }
        load_dotenv('local.env')
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
            )
        cursor = connection.cursor()
        cursor.execute(fetch_query)
        data = cursor.fetchall()
        self._df = pd.DataFrame(data, columns=['rating','recommend', 'validation_result', 'problem_category'])
        connection.commit()
        cursor.close()
        connection.close()
        

    def get_number_of_category(self, category):
        return len(self._df[self._df['problem_category'] == category])
    
    
    def get_total_number_of_entries(self):
        return len(self._df)
    
    
    def get_category_name(self, category):
        return self._problem_category_map.get(category, 'Unknown')
    
    
    def get_dataframe(self):
        return self._df
    
    
    def get_rating_percentages(self):
        percentages = self._df['rating'].value_counts(normalize=True) * 100
        return percentages, percentages.index
    
    
    def get_category_percentages(self):
        self._df['problem_category_mapped'] = self._df['problem_category'].apply(lambda x: self.get_category_name(x))
        jackets_category_counts = self._df['problem_category_mapped'].value_counts()
        percentages = (jackets_category_counts / len(self._df)) * 100
        return percentages, percentages.index
    
    
    def get_recommend_bar(self):
        recommend_counts = self._df['recommend'].value_counts()
        recommend_counts.index = recommend_counts.index.map({True: 'Yes', False: 'No'})
        return recommend_counts, recommend_counts.index
    
    
    