import sqlite3 as sq3

connection = sq3.connect("main.db")
cursor = connection.cursor()


def create_manga_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manga (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            
            name_rus        VARCHAR(256)    DEFAULT NULL,
            name_eng        VARCHAR(256)    DEFAULT NULL,
            type            VARCHAR(32)     DEFAULT NULL,
            release_year    VARCHAR(16)     DEFAULT NULL,
            status          VARCHAR(32)     DEFAULT NULL CHECK(status IN ("Finished", "", "Ongoing", "Frozen")),
            chapters_count  INTEGER         DEFAULT NULL,
            age_rating      VARCHAR(8)      DEFAULT NULL,
            description     TEXT            DEFAULT NULL,
            author          TEXT            DEFAULT NULL,
            img             TEXT            DEFAULT NULL,
            rating_id       INTEGER         DEFAULT NULL,
            
            FOREIGN KEY (rating_id) REFERENCES rating (id)
        )
    """)

    connection.commit()


def create_genre_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS genre (
            id              INTEGER PRIMARY KEY,
            name            VARCHAR(64) NOT NULL UNIQUE
        )
    """)

    connection.commit()


def create_manga_genre_table():
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS manga_genre (
                manga_id              INTEGER NOT NULL,
                genre_id              INTEGER NOT NULL,
                FOREIGN KEY (manga_id) REFERENCES manga (id),
                FOREIGN KEY (genre_id) REFERENCES genre (id),
                UNIQUE (manga_id, genre_id)
            )
        """)

    connection.commit()


def create_rating_table():
    cursor.execute("""
           CREATE TABLE IF NOT EXISTS rating (
               id              INTEGER PRIMARY KEY AUTOINCREMENT,
               rating_1        FLOAT,
               rating_2        FLOAT,
               rating_3        FLOAT
           )
       """)
    connection.commit()


create_manga_table()
create_genre_table()
create_manga_genre_table()
create_rating_table()

connection.close()
