#!/usr/bin/python

import psycopg2

conn = psycopg2.connect(database="plc_test", user="nm", password="postgres", host="127.0.0.1", port="4432")

print("Opened database successfully")


# Open a cursor to perform database operations
cur = conn.cursor()

query = "SELECT a.name as a_name, plc.name as plc_name, ST_Distance(a.geolocation, plc.geolocation) " \
        "as distance FROM dessert_after_meal a, dessert_after_meal plc " \
        "WHERE a.name='Bartaco' AND plc.name = 'Piece, Love, and Chocolate';"

# Query the database and obtain data as Python objects
cur.execute(query)
print(cur.fetchall())

# Make the changes to the database persistent
# conn.commit()

# Close communication with the database
cur.close()
conn.close()
