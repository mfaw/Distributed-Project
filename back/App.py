
from argparse import Namespace
from asyncio.log import logger
from distutils.log import debug
from gc import callbacks
from glob import glob
from http.client import OK
import mimetypes
from operator import truediv
from xml.dom.minidom import Document
from flask import Flask, request, jsonify, abort , send_file
from sqlalchemy import exc
from flask_cors import CORS
from database.model import db_drop_and_create_all, setup_db, Person
from authenticaiton.auth import CreateUserJWT , requires_auth , AuthError
import sys
import time
import os
import random
import datetime
from flask import session
from flask_socketio import SocketIO , send, emit , disconnect , join_room, leave_room
from flask_login import LoginManager , login_user , login_required, current_user , logout_user
from flask_pymongo import PyMongo
from flask_apscheduler import APScheduler

import requests


SECRETKEY = "qwlejlkasdlkjqwp"
app = Flask(__name__)
CORS(app)
setup_db(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Documents"
app.debug = True
mongo = PyMongo(app)
app.config['SECRET_KEY'] = SECRETKEY


cachedRooms = {}
cachedQuill = {}


def updateDB():
    global cachedQuill
    print("update database")
    for key in cachedQuill:
        result = mongo.db.Document.update_one({'name': key}, {'$set' :{'data' : cachedQuill[key]}})
    cachedQuill = {}



@app.route("/signup" , methods=['POST'])
def sign_up():
    payload = request.get_json()['Data']
    returned_jwt = CreateUserJWT()
    instance = Person.query.filter_by(username = payload['UserName']).first()
    instance2 = Person.query.filter_by(username = payload['Email']).first()
    if(instance !=None or instance2 !=None):
        time.sleep(0.5)
        return {'result' : False}
    else:
        try:
            person_user = Person(username=payload['UserName'], password = returned_jwt , email = payload["Email"])
            person_user.insert()
            time.sleep(0.5)
            return {'result' : True , "user" : person_user.print_self()}
        except:
            print(sys.exc_info())
            abort(400)

@app.route("/addDocumnet" , methods=['POST'])
def addDocument():
    documents = mongo.db.Document.find_one({"name" : request.get_json()['Data']})
    if(documents == None):
        mongo.db.Document.insert_one({"name" :  request.get_json()['Data'] , "Date" : "date" ,  "data" : {}} )
        return {'result':"created"}
    else:
         return {'result':"documentNameError"}

@app.route("/allDocuments" , methods=['GET'])
def getAllDocuments():
   
    documents = mongo.db.Document.find()
    data = []
    for i in documents:

        data.append({"name" : i['name'] , "date" : i['Date']})
    print(app.config["MONGO_URI"])
    return {'result':data}
    


# # sockets starts here


@app.route("/connect" , methods=['POST'])
def handle_message():
    payload = request.get_json()
    print("client connected " , payload['sid'])
    return {'result' : True}

@app.route("/disconnect" , methods=['POST'])
def test_disconnect():
    payload = request.get_json()
    print(payload)
    if(payload['sid'] in cachedRooms):
        room = cachedRooms[payload['sid']]
        return {'room' : room}
    else:
        return {'room' : "None"}



@app.route("/connectToRoom" , methods=['POST'])
def connectToNewRoom():
    payload = request.get_json()
    room = payload['room']
    sid = payload['sid']
    if(room in cachedQuill):
        cachedRooms[sid] = room
        print("new member joined the room")
        return {"data" : cachedQuill[room]}
    else:
        document = mongo.db.Document.find_one({"name" : room})
        if(document != None):
            cachedRooms[sid] = room
            print("new member joined the room")
            return {"data" : document['data']}


@app.route("/registerMouse" , methods=['POST'])
def registerMouse():
    payload = request.get_json()
    userId = payload['id']
    user =  Person.query.filter_by(id = userId).first()
    if(user != "None"):
        data = user.print_self()
        return {"name" : data['Username']}
    else:
         return {"name" : "None"}


@app.route("/leaveGroup" , methods=['POST'])
def leaveGroup():
    payload = request.get_json()
    print('session' , payload['sid'] , "left")
    return {"result" : True}





# here the Quill managemnt for documents
# so when we emit, we emit to document 
# sending changes to specific room
# listen to changes from client 

# # want to save our document by updating data of document
# # takes all our data
# # must be called from client

@app.route("/save_document" , methods=['POST'])
def save_document():
    name = request.get_json()['name']       
    data = request.get_json()['data']
    cachedQuill[name] = data
    return {"result" : True}

@app.route("/condition" , methods=['GET'])
def condition():
    return {"result" : True}

if __name__ == '__main__':
    scheduler = APScheduler()
    scheduler.add_job(func=updateDB, trigger='interval', id='job', seconds=8)
    scheduler.start()
    PORT = random.randint(5000,6000)

    url = 'http://127.0.0.1:5000/registerServer'
    myobj = {'port': PORT }
    x = requests.post(url, json = myobj)

    app.run(debug = False , port = PORT)



