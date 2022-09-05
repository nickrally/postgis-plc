import os
import logging
from flask import Flask, request, render_template, redirect, url_for
from wtforms import Form, StringField,  Field, validators
from wtforms.validators import InputRequired, Length
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_ , and_
from sqlalchemy.exc import IntegrityError, DataError
from dotenv import load_dotenv
import geocoder
from geoalchemy2.types import Geometry, Geography, func

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = 'dessertafterdinner'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


def getGeolocation(full_address):
    app.logger.info("Full address is: %s" % full_address)
    api_key = os.environ['BING_APIKEY']
    result = geocoder.bing(full_address, key=api_key)
    return result.json

class PlaceForm(FlaskForm):
    name = StringField('name')
    street_address = StringField('street_address')
    city = StringField('city')
    state = StringField('state')
    zip = StringField('zip', validators=[InputRequired(), Length(5)])


class Place(db.Model):
    __tablename__ = 'dessert_after_meal'
    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text,    unique=False, nullable=False)
    street_address =db.Column(db.Text, unique=False, nullable=False)
    city = db.Column(db.Text, unique=False, nullable=True)
    state = db.Column(db.Text, unique=True, nullable=False)
    zip = db.Column(db.Text, unique=True, nullable=False)
    geolocation = db.Column(Geography(geometry_type='POINT', srid=4326))

    def __init__(self, name=name, street_address=street_address, city=city, state=state, zip=zip, geolocation=geolocation):
        self.name = name
        self.street_address  = street_address
        self.city = city
        self.state = state
        self.zip = zip
        self.geolocation = geolocation


@app.route('/', endpoint='home', methods=['GET','POST'])
def index():
    places = Place.query.order_by(Place.id.desc())
    return render_template('home.html', places=places)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = PlaceForm(request.form)
    if request.method == 'POST':
        place = Place(form['name'].data, form['street_address'].data, form['city'].data,
                      form['state'].data, form['zip'].data)

        location = getGeolocation("%s, %s, %s %s"
                                 % (form['street_address'].data, form['city'].data, form['state'].data, form['zip'].data))
        app.logger.info("INSERT longitude: %s, latitude: %s" % (location['lng'], location['lat']))

        place.geolocation = "SRID=4326;POINT(%.9f %.9f)" %(location['lng'], location['lat'])

        db.session.add(place)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html', form=form)


@app.route('/edit/<string:id>', methods=['GET','POST'], endpoint='edit')
def edit(id):
    place = Place.query.get(id)
    form = PlaceForm(obj=place)
    if request.method == 'POST':
        form.populate_obj(place)

        location = getGeolocation("%s, %s, %s %s"
                                  % (
                                  form['street_address'].data, form['city'].data, form['state'].data, form['zip'].data))
        app.logger.info("UPDATE: longitude: %s, latitude: %s" % (location['lng'], location['lat']))

        place.geolocation = "SRID=4326;POINT(%.9f %.9f)" % (location['lng'], location['lat'])

        db.session.add(place)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', place=place, id=id, form=form)


@app.route('/delete/<int:id>', methods=['GET','POST'])
def delete(id):
    place = Place.query.get(id)
    if request.method == 'POST':
        db.session.delete(place)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('delete.html', place=place, id=id)


# @app.route('/search')
# def search():
#     places = None
#
#     def searchTitle():
#         txt = "%{}%".format(request.args.get('maxDistanceQuery'))
#         return Place.title.ilike(txt)
#
#     max_distance_selected = request.args.get('maxDistanceQuery')
#
#     if max_distance_selected:
#         query = Place.query.with_entities(Place, func.ST_Distance(Place.geolocation, coordinates_point).label(
#             'distance')).order_by('distance')
#         results = query.paginate(page, 10).items
#         for result in results:
#             event = result.Event
#             distance = result.distance
#             result_dict = event.to_dict()
#             result_dict['distance'] = distance


if __name__ == "__main__":
    app.run(debug=True)
