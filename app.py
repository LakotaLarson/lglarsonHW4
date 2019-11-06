from flask import Flask
from flask import render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import pymysql
import secrets

conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)

app = Flask(__name__)
app.config['SECRET_KEY']='SuperSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = conn
db = SQLAlchemy(app)

class lglarson_dogapp(db.Model):
    dogId = db.Column(db.Integer, primary_key=True)
    dogName = db.Column(db.String(255))
    age = db.Column(db.Integer)
    breed = db.Column(db.String(255))

    def __repr__(self):
        return "id: {0} | dog name: {1} | age: {2} | breed: {3}".format(self.id, self.dogName, self.age, self.breed)

class DogForm(FlaskForm):
    dogName = StringField('Dog Name:', validators=[DataRequired()])
    age = StringField('Age:', validators=[DataRequired()])
    breed= StringField('Breed: ', validators=[DataRequired()])

@app.route('/')
def index():
    all_dogs = lglarson_dogapp.query.all()
    return render_template('index.html', dogs=all_dogs, pageTitle='Lakota\'s Dogs')

@app.route('/add_dog', methods=['GET', 'POST'])
def add_dog():
    form = DogForm()
    if form.validate_on_submit():
        dog = lglarson_dogapp(dogName=form.dogName.data, age=form.age.data, breed=form.breed.data)
        db.session.add(dog)
        db.session.commit()
        return redirect('/')

    return render_template('add_dog.html', form=form, pageTitle='Add A New Dog')

if __name__ == '__main__':
    app.run(debug=True)
