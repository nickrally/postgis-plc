import os
from flask import Flask, request, render_template, redirect, url_for
from wtforms import Form, StringField,  Field, validators
from wtforms.validators import InputRequired, Length
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_ , and_
from sqlalchemy.exc import IntegrityError, DataError
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = 'dessertafterdinner'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


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

    def __init__(self, name=name, street_address=street_address, city=city, state=state, zip=zip):
        self.name = name
        self.street_address  = street_address
        self.city = city
        self.state = state
        self.zip = zip


@app.route('/', endpoint='home', methods=['GET','POST'])
def index():
    places = Place.query.order_by(Place.id.desc())
    return render_template('home.html', places=places)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        place = Place(request.form['name'], request.form['street_address'], request.form['city'],
                         request.form['state'], request.form['zip'])

        db.session.add(place)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html')


@app.route('/edit/<string:id>', methods=['GET','POST'], endpoint='edit')
def edit(id):
    place = Place.query.get(id)
    form = PlaceForm(obj=place)
    if request.method == 'POST':
        form.populate_obj(place)
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


if __name__ == "__main__":
    app.run(debug=True)
