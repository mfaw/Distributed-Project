
from argparse import Namespace
from asyncio.log import logger
from distutils.log import debug
from gc import callbacks
from http.client import OK
import mimetypes
from operator import truediv
from xml.dom.minidom import Document
from flask import Flask, request, jsonify, abort , send_file , render_template
from sqlalchemy import exc
from flask_cors import CORS
from database.model import db_drop_and_create_all, setup_db, Person
from authenticaiton.auth import CreateUserJWT , requires_auth , AuthError
import sys
import time
import os
import random
import datetime
PORT = None
from flask import session
from flask_socketio import SocketIO , send, emit , disconnect , join_room, leave_room
from flask_login import LoginManager , login_user , login_required, current_user , logout_user
from flask_pymongo import PyMongo
# import socketio as sk
from flask_script import Manager, Server

## we use flask for the backend as it's used to create web apps using python



SECRETKEY = "uqweiouioasjldkqwe"
# we create the app and open CORS and set up the db using mongodb for the documents
app = Flask(__name__)
# use cors (cross-origin resource sharing) bc server and client are on different ports
# cors is a mechanism that allows a server to indicate any origins other than its own from which a browser should permit loading resources
# this will allow to make request from different url to different url
CORS(app)
setup_db(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Documents"
# app.debug = True
mongo = PyMongo(app)
# login manager contains the code that makes app and flask workr together
login_manager = LoginManager()
login_manager.login_view = 'logoutUseer'
login_manager.init_app(app)

## adding flask-socketio to our flask app
app.config['SECRET_KEY'] = SECRETKEY
# we allow cors and make async handlers to false to give each client one handler only not concurrent handlers for the same event
socketio = SocketIO(app , logger = False , cors_allowed_origins="*" , async_handlers=False , static_folder='../build', static_url_path='/')

# create route when add document is posted from client
# a POST request will be made and document will be persisted to DB
# login is required to add document
@app.route("/addDocumnet" , methods=['POST'])
@login_required
def addDocument():
    # mongo db is the DB that has all documents 
    # find the name of the name of document typed in by user in input box in the mongodb
    documents = mongo.db.Document.find_one({"name" : request.get_json()['Data']})
    # if name is not in DB, none is returned
    if(documents == None):
        # insert new document in DB with name typed by user and data is blank
        mongo.db.Document.insert_one({"name" :  request.get_json()['Data'] , "Date" : "date" ,  "data" : {}} )
        # new document is created
        return {'result':"created"}
    else:
        # else if name is in DB, return document name error
         return {'result':"documentNameError"}

# create route when all documents is requested from client
# a GET request will be made and document will be get from DB
# login is required to add document
@app.route("/allDocuments" , methods=['GET'])
@login_required
def getAllDocuments():
   # find all documents in DB
    documents = mongo.db.Document.find()
    data = []
    # loop over all documents gotten from DB and append them to data
    for i in documents:

        data.append({"name" : i['name'] , "date" : i['Date']})
        # return data to user
    return {'result':data}
    

def ack():
    print('message was received!')

# socket recieve connectToRoom message from client
# connect document to new room with the same name as document
@socketio.on('connectToRoom')
@authenticated_only
def connectToNewRoom(objectData):
    # search for document with given room id which is the document name
    document = mongo.db.Document.find_one({"name" : objectData['room']})
    # if document exists
    if(document != None):
        # client will join room -- room name is the document name
        join_room(objectData['room'])
        # add session for client with the room
        cachedRooms[request.sid] = objectData['room']
        print("new member joined")
        # emit document data and client id to client
        emit('reciveDocument' , {"data" : document['data'] , "sid" : request.sid})


############################# QUILL SOCKET MANAGEMENT ###############################
# so when we emit, we emit to document 
# sending changes to specific room
# listen to changes from client 
@socketio.on('send-changes')
@authenticated_only
def registerMouse(objectData):
    room = objectData['room']
    delta = objectData['delta']
    print(delta)
    # broadcast message to everyone else thatis in the room that there are changes which is delta
    emit('receive-changes' , {"sid" : request.sid , 'delta' : delta} , room = room)

# want to save our document by updating data of document
# takes all our data
# must be called from client
@socketio.on('save-document')
@authenticated_only
def registerMouse(objectData):
    name = objectData['name']
    data = objectData['data']
    # update document in DB
    result = mongo.db.Document.update_one({'name': name}, {'$set' :{'data' : data}})
    print(result)
    # broadcast message to everyone else that there are changes which is delta
    # emit('receive-changes' , {"sid" : request.sid , 'delta' : delta} , room = room)

############################## ERROR HANDLERS ########################################## 

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
    }), 400


@app.errorhandler(412)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 412,
        "message": "Precondition for resouce failed",
        "question": False
    }), 412


@app.errorhandler(404)
def error_resource_not_found(error):
    return jsonify({
        "success": False,
        "message": "Resource not found",
        "error": 404
    }), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "message": "Internal server error",
        "error": 500
    }), 500


@app.errorhandler(422)
def not_processable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Request cant be processed"
    }), 422


@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405

@app.errorhandler(401)
def auth_error(error):
    return jsonify({
        "success":False,
        "error":401,
        "message":"Not Authorized"
    })
@app.errorhandler(403)
def auth_error(error):
    return jsonify({
        "success":False,
        "error":403,
        "message":"Forbidden"
    }),403
@app.errorhandler(AuthError)
def auth_error(error):
    print(error) 
    return jsonify({
        "success":False,
        "error":error.status_code,
        "message":error.error
    }),error.status_code    




# manager = Manager(app)
# manager.add_command('runserver', CustomServer())

if __name__ == '__main__':
    PORT = random.randint(5000,6000)
    sio.connect('http://127.0.0.1:5002')
    sio.emit('registerport' , {"port" : 5004})
    socketio.run(app , port = 5004 , debug = True)
    
    # manager.run()
    # sio.disconnect()




