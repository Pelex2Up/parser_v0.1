import psycopg2

DBNAME = 'parser_db'
USER = 'postgres'
PASSWORD = 'postgres'
HOST = '127.0.0.1'


def create_flats_table():
    with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
        with conn.cursor() as cur:
            cur.execute('''
            CREATE TABLE IF NOT EXISTS flats(
                id serial PRIMARY KEY,
                link CHARACTER VARYING(300) UNIQUE NOT NULL,
                reference CHARACTER VARYING(30),
                price INTEGER,
                title CHARACTER VARYING(1000),
                description CHARACTER VARYING(3000),
                date TIMESTAMP WITH TIME ZONE,
                space CHARACTER VARYING(30),
                city CHARACTER VARYING(50),
                street CHARACTER VARYING(100),
                area CHARACTER VARYING(100),
                year INTEGER,
                rooms INTEGER,
                phone_num CHARACTER VARYING(100)
                )''')


def insert_flat(flat):
    with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO flats (link, reference, price, title, description, date, space, city, street,
                area, year, rooms, phone_num) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (link) DO UPDATE 
                SET 
                link = EXCLUDED.link, 
                price = EXCLUDED.price, 
                title = EXCLUDED.title, 
                description = EXCLUDED.description, 
                date = EXCLUDED.date,
                space = EXCLUDED.space,
                city = EXCLUDED.city,
                street = EXCLUDED.street,
                area = EXCLUDED.area,
                year = EXCLUDED.year,
                rooms = EXCLUDED.rooms,
                phone_num = EXCLUDED.phone_num
                 ''',
                        (flat.link, flat.reference, flat.price, flat.title, flat.description, flat.date,
                         flat.space, flat.city, flat.street, flat.area, flat.year, flat.rooms, flat.phone_num)
                        )