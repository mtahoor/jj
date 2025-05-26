import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect to PostgreSQL server
conn = psycopg2.connect(
    dbname='postgres',
    user='admin',
    password='admin',
    host='localhost',
    port='5432'
)

conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

# Create the database
try:
    cursor.execute('CREATE DATABASE eodb_rest2')
    print("Database 'eodb_rest2' created successfully!")
except psycopg2.errors.DuplicateDatabase:
    print("Database 'eodb_rest2' already exists.")
except Exception as e:
    print(f"An error occurred: {e}")

# Close the connection
cursor.close()
conn.close()
