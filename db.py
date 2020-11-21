import os  # Standard library
import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(user=os.getenv('DB_USER'),
                            password=os.getenv('DB_PASS'),
                            host=os.getenv('DB_HOST'),
                            port="5432",
                            database=os.getenv('DB_NAME'))

    cursor = conn.cursor()

    create_table_query = ''' 
    CREATE TABLE watchlist
    (ID INT PRIMARY KEY     NOT NULL,
    DISCORDId           TEXT    NOT NULL,
    PRIC         REAL); '''

    cursor.execute(create_table_query)
    conn.commit()
    print("Table created successfully in PostgreSQL ")
    cursor.close()
    conn.close()
    print("PostgreSQL connection is closed")
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)


