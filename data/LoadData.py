import sqlite3 as sq3
import json

connection = sq3.connect("main.db")
cursor = connection.cursor()

site_data_paths = ["../Parsers/Mangabuff/MangabuffData.json", "../Parsers/Remanga/RemangaData.json", "../Parsers/Nighthub/NighthubData.json"]

def is_manga_in_database(manga: dict) -> int:
    cursor.execute(f"""
        SELECT id FROM manga
        WHERE (name_rus = "{manga["name_rus"]}" and release_year = '{manga["manga_release_year"]}')
        OR (name_eng = "{manga["name_eng"]}" and release_year = '{manga["manga_release_year"]}')
    """)

    f = cursor.fetchall()
    if f:
        return f[0][0]
    return 0


def update_manga(manga_id: int, manga: dict, site_id: int) -> None:
    cursor.execute(f"""
        SELECT rating_id FROM manga
        WHERE id = {manga_id}
    """)
    rating_id = cursor.fetchall()[0][0]
    update_rating(rating_id, manga["score"], site_id)

    cursor.execute(f"""
        UPDATE manga
        SET author = CASE WHEN author = "" THEN '{manga["author"]}' ELSE author END,
            name_eng = CASE WHEN name_eng = "" THEN "{manga["name_eng"]}" ELSE name_eng END,
            age_rating = CASE WHEN age_rating = "" THEN '{manga["age_rating"]}' ELSE age_rating END
        WHERE id = {manga_id}
    """)

    insert_genres(manga["tags"])
    insert_manga_genres(manga_id, manga["tags"])

    connection.commit()


def insert_new_manga(manga: dict, site_id: int) -> None:
    rating_id = insert_rating(manga["score"], site_id)

    # Insert manga data
    cursor.execute(f"""
        INSERT INTO manga (name_rus, name_eng, type, release_year, status, chapters_count, age_rating, description, author, img, rating_id)
        VALUES ("{manga["name_rus"]}", "{manga["name_eng"]}", '{manga["manga_type"]}', '{manga["manga_release_year"]}', '{manga["manga_status"]}', '{manga["chapters_count"]}', '{manga["age_rating"]}', '{manga["description"]}','{manga["author"]}', '{manga["image_url"]}', {rating_id})
    """)

    manga_id = cursor.lastrowid
    insert_genres(manga["tags"])
    insert_manga_genres(manga_id, manga["tags"])

    connection.commit()


def insert_manga_genres(manga_id: int, tags: list) -> None:
    genre_ids = cursor.execute(f"""
        SELECT id FROM genre
        WHERE name IN ("{'","'.join(tags)}")
    """)
    genre_ids = genre_ids.fetchall()
    genre_ids = [genre_ids[i][0] for i in range(len(genre_ids))]

    # Fill the manga-genre table
    for i in genre_ids:
        cursor.execute(f"""
            INSERT OR IGNORE INTO manga_genre
            VALUES ('{manga_id}', '{i}')
        """)


def insert_genres(tags: list) -> None:
    for i in tags:
        cursor.execute(f"""
            INSERT OR IGNORE INTO genre (name)
            VALUES ('{i}')
        """)


def insert_rating(score: float, site_id: int) -> int:
    rating_value = [0, 0, 0]
    rating_value[site_id - 1] = score
    cursor.execute(f"""
        INSERT INTO rating (rating_1, rating_2, rating_3)
        VALUES ({rating_value[0]}, {rating_value[1]}, {rating_value[2]})
    """)

    return cursor.lastrowid


def update_rating(rating_id: int, score: float, site_id: int) -> None:
    cursor.execute(f"""
        UPDATE rating
        SET rating_{site_id} = {score}
        WHERE id = {rating_id}
    """)


def add_manga(manga: dict, site_id: int) -> None:
    manga_id = is_manga_in_database(manga)
    if manga_id:
        update_manga(manga_id, manga, site_id)
    else:
        insert_new_manga(manga, site_id)


for i in range(len(site_data_paths)):
    with open(site_data_paths[i], "r", encoding="utf-8") as file:
        manga_data_list = json.load(file)
    for manga in manga_data_list:
        print(manga["name_rus"])
        add_manga(manga, i + 1)

connection.close()
