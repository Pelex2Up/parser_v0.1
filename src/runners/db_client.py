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


def get_all_not_posted_flats(parser_types):
    with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
        with conn.cursor() as cur:
            cur.execute('''
                    SELECT link, reference, price, title, description, date, photo_links, id FROM flats
                    WHERE (is_tg_posted = false or is_tg_posted IS NULL) 
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
