from flask import Flask
from flask import render_template, redirect, request, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import pymysql
import secrets

conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)


app = Flask(__name__)
app.config['SECRET_KEY']='SuperSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = conn
db = SQLAlchemy(app)
'''
#for when pushed to Azure
conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)

app = Flask(__name__)
app.config['SECRET_KEY']='SuperSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = conn
db = SQLAlchemy(app)
'''
class lglarson_dogapp(db.Model):
    dogId = db.Column(db.Integer, primary_key=True)
    dogName = db.Column(db.String(255))
    age = db.Column(db.Integer)
    breed = db.Column(db.String(255))

    def __repr__(self):
        return "id: {0} | dog name: {1} | age: {2} | breed: {3}".format(self.id, self.dogName, self.age, self.breed)

class DogForm(FlaskForm):
    dogId = IntegerField('Dog ID: ')
    dogName = StringField('Dog Name:', validators=[DataRequired()])
    age = IntegerField('Age:', validators=[DataRequired()])
    breed= StringField('Breed: ', validators=[DataRequired()])

@app.route('/')
def index():
    all_dogs = lglarson_dogapp.query.all()
    return render_template('index.html', dogs=all_dogs, pageTitle='Lakota\'s Dogs')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method =='POST':
        form = request.form
        search_value = form['search_string']
        search = "%{0}%".format(search_value)
        results = lglarson_dogapp.query.filter( or_(lglarson_dogapp.dogName.like(search), lglarson_dogapp.breed.like(search))).all()
        return render_template('index.html', dogs=results, pageTitle='Lakota\'s Dogs', legend='Search Results')
    else:
        return redirect('/')



@app.route('/add_dog', methods=['GET', 'POST'])
def add_dog():
    form = DogForm()
    if form.validate_on_submit():
        dog = lglarson_dogapp(dogName=form.dogName.data, age=form.age.data, breed=form.breed.data)
        db.session.add(dog)
        db.session.commit()
        print('Dog was successully added!')
        return redirect('/')

    return render_template('add_dog.html', form=form, pageTitle='Add A New Dog')

@app.route('/delete_dog/<int:dogId>', methods=['GET','POST'])
def delete_dog(dogId):
    if request.method == 'POST': #if it's a POST request, delete the friend from the database
        obj = lglarson_dogapp.query.filter_by(dogId=dogId).first()
        db.session.delete(obj)
        db.session.commit()
        flash('Dog was successfully deleted!')
        return redirect("/")

    else: #if it's a GET request, send them to the home page
        return redirect("/")

@app.route('/dog/<int:dogId>', methods=['GET', 'POST'])
def dog(dogId):
    dog = lglarson_dogapp.query.get_or_404(dogId)
    return render_template('dog.html', form=dog, pageTitle='Dog Details', legend="Dog Details")

@app.route('/dog/<int:dogId>/update', methods=['GET','POST'])
def update_dog(dogId):
    dog = lglarson_dogapp.query.get_or_404(dogId)
    form = DogForm()

    if form.validate_on_submit():
        dog.dogId = form.dogId.data
        dog.dogName = form.dogName.data
        dog.age = form.age.data
        dog.breed = form.breed.data
        db.session.commit()
        return redirect('/')

    form.dogId.data = dog.dogId
    form.dogName.data = dog.dogName
    form.age.data = dog.age
    form.breed.data = dog.breed
    return render_template('update_dog.html', form=form, pageTitle='Update Post',legend="Update A Dog")

if __name__ == '__main__':
    app.run(debug=True)
