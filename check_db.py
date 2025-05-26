import os
import django
import psycopg2
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Get database settings
db_settings = settings.DATABASES['default']

# Connect to the database
conn = psycopg2.connect(
    dbname=db_settings['NAME'],
    user=db_settings['USER'],
    password=db_settings['PASSWORD'],
    host=db_settings['HOST'],
    port=db_settings['PORT']
)

# Create a cursor
cur = conn.cursor()

# Query to list all tables
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name;
""")

# Fetch all results
tables = cur.fetchall()

# Print the tables
print("Tables in the database:")
for table in tables:
    print(f"- {table[0]}")

# Close the cursor and connection
cur.close()
conn.close()
