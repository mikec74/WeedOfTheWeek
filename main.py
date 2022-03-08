from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap(app)


# CONNECT TO DB
# The current version of SQLAlchemy uses a URI of "postgresql://" when accessing a PostgreSQL database.
# Heroku uses a URI of "postgres://". Because of this difference, when running at Heroku, the system
# crashes because SQLAlchemy cannot connect to a URI of "postgres://". I added the replace() call to change
# the environment variable returned from Heroku into a URI that can be used by SQLAlchemy. If Heroku ever
# changes to use "postgresql://" like SQLAlchemy does, then this code should still work since the replace()
# call will not change the URI. If Heroku ever makes this change, you can remove the call to replace().
# This code was suggested by a post on StackOverflow:
#     https://stackoverflow.com/questions/66690321/flask-and-heroku-sqlalchemy-exc-nosuchmoduleerror-cant-load-plugin-sqlalchemy
#
# Running the program on my local computer uses a SQLite database. I want to continue to be able to run the
# program on my computer for development while it is also running on Heroku. This is accomplished by including
# the DATABASE_URL in an environment variable. The call to replace() has no effect on this URL because the
# URL on the local computer does not contain "postgres://".
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL",
).replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class PageHeader(db.Model):
    __tablename__ = "page_headers"
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(100), nullable=False)


class Weed(db.Model):
    __tablename__ = "weeds"
    id = db.Column(db.Integer, primary_key=True)
    scientific_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    removal_method = db.Column(db.Text, nullable=False)
    comments = db.Column(db.Text, nullable=False)
    location_desc = db.Column(db.Text, nullable=False)
    location_map = db.Column(db.String(200), nullable=False)
    display_order = db.Column(db.Integer, nullable=False)


class WeedCommonName(db.Model):
    __tablename__ = "weed_common_names"
    id = db.Column(db.Integer, primary_key=True)
    common_name = db.Column(db.String(250), nullable=False)
    is_primary = db.Column(db.Boolean, nullable=False)
    weed_id = db.Column(db.Integer, db.ForeignKey("weeds.id"), nullable=False)

    weed = db.relationship("Weed", backref=db.backref("weed_common_names", lazy=True))


class WeedPhoto(db.Model):
    __tablename__ = "weed_photos"
    id = db.Column(db.Integer, primary_key=True)
    photo_url = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.String(250), nullable=False)
    display_order = db.Column(db.Integer, nullable=False)
    weed_id = db.Column(db.Integer, db.ForeignKey("weeds.id"), nullable=False)

    weed = db.relationship("Weed", backref=db.backref("weed_photos"), lazy=True)


db.create_all()


@app.template_filter("comma_separated")
def comma_separated(names):
    is_first = True
    comma_separated_list = ""
    for name in names:
        if not name.is_primary:
            if is_first:
                is_first = False
            else:
                comma_separated_list += ", "
            comma_separated_list += name.common_name
    return comma_separated_list


@app.route('/')
def show_page():
    header = PageHeader.query.first()
    all_weeds = Weed.query.order_by(Weed.display_order).all()
    return render_template("index.html",
                           header=header,
                           all_weeds=all_weeds,
                           current_year=datetime.utcnow().year
                           )


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
