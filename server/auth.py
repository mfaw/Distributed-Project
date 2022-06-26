
import email
from msilib.schema import InstallUISequence
from operator import truediv
from pickle import PERSID
from winreg import REG_QWORD
from flask import request
from functools import wraps
from flask import abort
import jwt
from database.model import db_drop_and_create_all, setup_db, Person
SECRET = "secret code no one knows"

def CreateUserJWT():
    payload = request.get_json()['Data']
    payload = {'UserName' : payload['UserName'] , 'Password' : payload['Password']}
    encoded_jwt = jwt.encode(payload, SECRET, algorithm="HS256")
    return encoded_jwt
    
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code
    def __repr__(self):
        return 'class'+str(self.error)+" code "+str(self.status_code)+' what'


def get_token_auth_header():
    payload = request.get_json()['Data']
    payload = {'UserName' : payload['UserName'] , 'Password' : payload['Password']}
    encoded_jwt = jwt.encode(payload, SECRET, algorithm="HS256")
    instance = Person.query.filter_by(username = payload['UserName'] , password = encoded_jwt).first()
    if (instance): return instance
    else: return False


def requires_auth():
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args , **kwargs):
            token_valid = get_token_auth_header()
            print(token_valid)
            return f(token_valid , *args , **kwargs)
        return wrapper
    return requires_auth_decorator

