import psycopg2

conn = psycopg2.connect(dbname="postgres", user="postgres", password="1234", host="localhost")
conn.autocommit = True

cursor = conn.cursor()
cursor.execute("CREATE DATABASE mydatabase;")
cursor.close()
conn.close()

print("База данных успешно создана")
