import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import json
from flask_login import UserMixin
database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

## SQL for python database
db = SQLAlchemy()

## set up the database
def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

## create person (user) in db
class Person(db.Model , UserMixin):
    ## user will have id(primary key), username(unique), email(unique), and password
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    username = Column(String(), unique=True)
    password =  Column(String(), nullable=False)
    email = Column(String() , nullable=False , unique=True)
    
    def print_self(self):
        return {
            'id': self.id,
            'Username': self.username,
            'Email': self.email
        }

    ## insert user in person table
    def insert(self):
        db.session.add(self)
        db.session.commit()

    ## delete user record from person table  
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    ## update user session
    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.print_self())