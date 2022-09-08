## My first postGIS project: Flask app with postgresql backend

Full CRUD (create, read, update, delete).
Currenty hosted on Heroku: https://plc-after-dinner.herokuapp.com/
Search restaurants within whatever distnce (in meters) from PLC (Piece, Love & Chocolate shop on Pearl St in Boulder, CO)
Heroku actually supports instlling postgis extension.
From Heroku CLI:

```
psql (13.2, server 14.4 (Ubuntu 14.4-1.pgdg20.04+1))
WARNING: psql major version 13, server major version 14.
         Some psql features might not work.
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits: 256, compression: off)
Type "help" for help.

plc-after-dinner::DATABASE=> CREATE EXTENSION postgis;
CREATE EXTENSION
```

![Alt text](/static/imag/screenshot1.png "screenshot")

### Create a table in a database with postgis extension:

```buildoutcfg
plc_test=# CREATE TABLE dessert_after_meal (
    id SERIAL PRIMARY KEY, name TEXT NOT NULL,
    street_address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip TEXT NOT NULL
);
```

### Insert initial data

```
plc_test=# INSERT INTO dessert_after_meal (name, street_address, city, state, zip)
    VALUES ('Piece, Love, and Chocolate', '805 Pearl St.', 'Boulder', 'CO', '80302');

plc_test=# INSERT INTO dessert_after_meal (name, street_address, city, state, zip)
    VALUES ('Roadhouse Boulder Depot', '2366 Junction Pl.', 'Boulder', 'CO', '80301');

plc_test=# INSERT INTO dessert_after_meal (name, street_address, city, state, zip)
    VALUES ('Spruce Farm and Fish', '2115 13th St.', 'Boulder', 'CO', '80302');

plc_test=# INSERT INTO dessert_after_meal (name, street_address, city, state, zip)
    VALUES ('Bartaco', '1048 Pearl St.', 'Boulder', 'CO', '80302');
```

### Get latitude and longitude using Bing Maps Api with free apikey

```buildoutcfg
plc % python3

>>> import geocoder

>>> key = 'AbC...'

>>> plc_address = '805 Pearl Street, Boulder, CO, 80302'
>>> g_plc = geocoder.bing(plc_address, key=key)
>>> results_plc = g_plc.json
>>> print(results_plc['lat'], results_plc['lng'])

40.017133 -105.284773

>>> rhbd_address = '2366 Junction Pl, Boulder, CO 80301'
>>> g_rhbd = geocoder.bing(rhbd_address, key=key)
>>> results_rhbd = g_rhbd.json
>>> print(results_rhbd['lat'], results_rhbd['lng'])

40.024896 -105.251041

>>> sff_address = '2115 13th St, Boulder, CO 80302'
>>> g_sff = geocoder.bing(sff_address, key=key)
>>> results_sff = g_sff.json
>>> print(results_sff['lat'], results_sff['lng'])

40.019434 -105.279445

>>> bt_address = '1048 Pearl St Suite 101, Boulder, CO 80302'
>>> g_bt = geocoder.bing(bt_address, key=key)
>>> results_bt = g_bt.json
>>> print(results_bt['lat'], results_bt['lng'])

40.017207 -105.28182
```

### Alter table, add a column of type `GEOGRAPHY`

```buildoutcfg
plc_test=# ALTER TABLE dessert_after_meal ADD COLUMN geolocation GEOGRAPHY(POINT);
```

### Update rows

```buildoutcfg
plc_test=# UPDATE dessert_after_meal SET geolocation = 'point(-105.284773 40.017133)'  WHERE id=1;
plc_test=# UPDATE dessert_after_meal SET geolocation = 'point(-105.251041 40.024896)'  WHERE id=2;
plc_test=# UPDATE dessert_after_meal SET geolocation = 'point(-105.279445 40.019434)'  WHERE id=3;
plc_test=# UPDATE dessert_after_meal SET geolocation = 'point(-105.28182 40.017207)'  WHERE id=4;
```

### Iterate over restaurant rows to calculate distance to the chocolate shop

```buildoutcfg
plc_test=# SELECT a.name, ST_Distance(a.geolocation, plc.geolocation) as distance FROM dessert_after_meal AS a JOIN dessert_after_meal AS plc ON a.id <> plc.id WHERE plc.name = 'Piece, Love, and Chocolate' ORDER BY distance;


          name           |   distance
-------------------------+---------------
 Bartaco                 |  252.23875067
 Spruce Farm and Fish    |  521.69999719
 Roadhouse Boulder Depot | 3005.86236497
(3 rows)
```

### Find a restaurant within 500 meters (546 yards) from the chocolate shop

```buildoutcfg
plc_test=# SELECT a.name, ST_Distance(a.geolocation, plc.geolocation) as distance FROM dessert_after_meal AS a JOIN dessert_after_meal AS plc ON a.id <> plc.id WHERE plc.name = 'Piece, Love, and Chocolate' AND ST_Distance(a.geolocation, plc.geolocation) < 500 ORDER BY distance;

  name   |   distance
---------+--------------
 Bartaco | 252.23875067
(1 row)
```

Bartaco is my first choice anyway!
