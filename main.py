import sqlite3
from flask import g, render_template, request
from flask import Flask
from urllib3 import request

app = Flask(__name__)

DATABASE = 'data/main.db'


@app.route("/")
def main_page():
    manga_list = query_db("select * from manga")
    return render_template('index.html', manga_list=manga_list)


@app.route("/manga_id=<manga_id>")
def manga_page(manga_id):

    manga = query_db(f"select * from manga where id = {manga_id}")
    rating = query_db(f"select * from rating where id = {manga_id}")
    tags = query_db(f"SELECT * FROM genre g JOIN manga_genre mg ON g.id = mg.genre_id WHERE mg.manga_id = {manga_id}")
    return render_template('manga.html', manga=manga[0], rating=rating[0], tags=tags)

@app.route("/tag_id=<tag_id>")
def filter_tag(tag_id):

    manga_list = query_db(f"SELECT * FROM manga m JOIN manga_genre mg ON m.id = mg.manga_id WHERE mg.genre_id = {tag_id}")

    return render_template('index.html', manga_list=manga_list)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

    db.row_factory = sqlite3.Row

    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
