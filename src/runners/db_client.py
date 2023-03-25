import psycopg2
import psycopg2.extras

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
                phone_num CHARACTER VARYING(100),
                images CHARACTER VARYING
                )''')


def insert_flat(flat):
    with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO flats (link, reference, price, title, description, date, space, city, street,
                area, year, rooms, phone_num, photo_links) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
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
                         flat.space, flat.city, flat.street, flat.area, flat.year, flat.rooms, flat.phone_num,
                         ','.join(flat.images))
                        )


def get_all_not_posted_flats(parser_types) -> list:
    with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
        with conn.cursor() as cur:
            cur.execute('''
                    SELECT link, reference, price, title, description, date, photo_links, id, is_archive FROM flats
                    WHERE (is_tg_posted = false and is_archive = false) 
                    and reference IN %(parser_types)s
                 ''',
                        {'parser_types': tuple(parser_types)}
                        )
            return cur.fetchall()


def update_is_posted_state(ids):
    with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
        with conn.cursor() as cur:
            cur.execute('''
                    UPDATE flats SET
                    is_tg_posted = true
                    WHERE id = ANY(%s)
                 ''',
                        [ids, ]
                        )


def insert_batch(flats_list):
    with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
        with conn.cursor() as cur:
            query = """INSERT INTO flats (link, reference, price, title, description, date, space, city, street,
                        area, year, rooms, phone_num, photo_links) VALUES %s
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
                        phone_num = EXCLUDED.phone_num"""
            psycopg2.extras.execute_values(cur, query, flats_list, page_size=100)


def get_all_flats():
    with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM flats""")
            flats = cur.fetchall()
            return flats
