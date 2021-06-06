from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
import string
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Urls(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key=True)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String(10))

    def __init__(self, long, short):
        self.long = long
        self.short = short

@app.before_first_request
def create_tables():
    db.create_all()

def shorten_url():
    letters = string.ascii_lowercase+string.ascii_uppercase
    while True:
        rand_letters = random.choices(letters, k=3)
        rand_letters = "".join(rand_letters)
        short_url = Urls.query.filter_by(short=rand_letters).first()
        if not short_url:
            return rand_letters
    


@app.route('/', methods=['POST','GET'])
def home():
    if request.method == "POST": # get data from the form
        url_received = request.form["nm"]
        found_url = Urls.query.filter_by(long=url_received).first()
        if found_url:
            return redirect(url_for("display_short_url", url=found_url.short))
        else:
            short_url = shorten_url()
            new_url = Urls(url_received, short_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for("display_short_url", url=short_url))
    else:
        return render_template('index.html')

@app.route('/display/<url>')
def display_short_url(url):
    return render_template('short.html',short_url_display=url)

@app.route('/<short_url>')
def redirection(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        return redirect(long_url.long)
    else:
        return f'<h1>URL dosen\'t Exist</h1>'

@app.route('/all_urls')
def display_all():
    return render_template('allurls.html',val=Urls.query.all())

@app.route('/delete/<int:id_>')    
def deleteurl(id_):
    url_to_remove = Urls.query.filter_by(id_=id_).first()
    db.session.delete(url_to_remove)
    db.session.commit()
    return redirect("/all_urls")

if __name__ == "__main__":
    app.run(debug=True)