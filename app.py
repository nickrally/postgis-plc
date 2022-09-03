from flask import Flask, request, render_template
from wtforms import Form, StringField,  Field, validators
from wtforms.validators import InputRequired, Length
from flask_wtf import FlaskForm

app = Flask(__name__)
app.secret_key = b'ZsbK\x9fdD|`\x07\x05\x01\x95\x93u\xae'

class AddressForm(FlaskForm):
    name     = StringField('name')
    street_address = StringField('street_address')
    city    = StringField('city')
    state = StringField('state')
    zipcode = StringField('zipcode', validators=[InputRequired(),
                                            Length(5)])


# @app.route('/')
# def index():
#     return render_template('home.html')

@app.route('/', methods=['GET','POST'])
def index():
    form = AddressForm(request.form)
    if request.method == 'POST' and form.validate():
        return render_template('home.html')
    return render_template('home.html', form=form)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == "__main__":
    app.run(debug=True)
