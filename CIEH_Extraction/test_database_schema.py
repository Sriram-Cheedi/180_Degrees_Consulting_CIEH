
from src.database.connection import get_connection
from src.database.schema import create_tables


create_tables()

connection = get_connection()

tables = connection.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
      AND name NOT LIKE 'sqlite_%'
    ORDER BY name
""").fetchall()

print("Database tables:")

for table in tables:
    print("-", table["name"])

connection.close()
