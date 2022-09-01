import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(os.environ['DATABASE_URL'])

cur = conn.cursor()

query1 = "SELECT name, ST_Distance(a.geolocation, plc.geolocation) as distance FROM dessert_after_meal a, " \
         "LATERAL (SELECT id, geolocation FROM dessert_after_meal " \
         "WHERE name = 'Piece, Love, and Chocolate') AS plc " \
         "WHERE a.id <> plc.id ORDER BY distance;"

cur.execute(query1)

message1 = "Dessert after dinner - distances between Piece, Love & Chocolate and three restaurants"
print(f'{message1}\n{cur.fetchall()}')

query2 = "SELECT name, ST_Distance(a.geolocation, plc.geolocation) as distance FROM dessert_after_meal a, " \
         "LATERAL (SELECT id, geolocation FROM dessert_after_meal " \
         "WHERE name = 'Piece, Love, and Chocolate') AS plc " \
         "WHERE a.id <> plc.id AND ST_Distance(a.geolocation, plc.geolocation) < 500 ORDER BY distance;"

cur.execute(query2)

message2 = "Dessert after dinner - which of the three restaurants is within 500 meters from Piece, Love & Chocolate?"
print(f'{message2}\n{cur.fetchall()}')

cur.close()
conn.close()
