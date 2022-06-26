
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
# db_drop_and_create_all()
# hash tables used for caching
cachedRooms = {}
# sio = sk.Client()


# def custom_call():
#     sio.connect('http://127.0.0.1:5000/')
#     sio.emit('registerport' , {"port" : PORT})
# class CustomServer(Server):
#     def __call__(self, app, *args, **kwargs):
#         custom_call()
#         #Hint: Here you could manipulate app
#         return Server.__call__(self, app, *args, **kwargs)

# with app.app_context():
#     print("heherlkalerj")

# @sio.event
# def connect():
#     print("I'm connected!")

# @sio.event
# def connect_error(data):
#     print("The connection failed!")

# @sio.event
# def disconnect():
#     print("I'm disconnected!")
        

# load user by querying it from Person table in sqlalchemy database to get user id
@login_manager.user_loader
def load_user(user_id):
    return Person.query.get(int(user_id))

def random_image():
    """
    Return a random image from the ones in the static/ directory
    """
    img_dir = "./static"
    img_list = os.listdir(img_dir)
    img_path = os.path.join(img_dir, random.choice(img_list))
    return img_path


@app.route("/image/cat")
def returnMessage():
    image = random_image()
    return send_file(image , mimetype = "image/jpg")

# create route to logout, must be logged in
@app.route("/logout")
@login_required
def logoutUseer():
    if(current_user.is_authenticated):
        # logout user of flask-login
        logout_user()
    
    return {"result" : "loginError"}

# signing in requires authorization
# create route when user submits sign in data, a POST request will be made and data will be persisted to DB
@app.route("/signin" , methods=['POST'])
@requires_auth()
def sign_in(instance):
    # instance is form data, username and password
    if (instance):
        # remember the user details and data persisted to DB
        login_user(instance, remember=True)
        data = { 
            "result" : True,
        }
        time.sleep(0.5)
        return data
    else:
        # else result is false
        time.sleep(0.5)
        return {'result' : False}

# create route when user submits sign up data,  a POST request will be made and data will be persisted to DB
@app.route("/signup" , methods=['POST'])
def sign_up():
    # get data of form
    payload = request.get_json()['Data']
    # create user json web token
    returned_jwt = CreateUserJWT()
    # query the username and email in the person table (sqlalchemy db of users)
    instance = Person.query.filter_by(username = payload['UserName']).first()
    instance2 = Person.query.filter_by(username = payload['Email']).first()
    # if query return data, then username or email already exist
    if(instance !=None or instance2 !=None):
        time.sleep(0.5)
        # return false
        return {'result' : False}
    else:
        # else if the query in instance and instance2 return none, then no user exists with the username or email
        try:
            # new record in person table with username and email and password entered in the form
            person_user = Person(username=payload['UserName'], password = returned_jwt , email = payload["Email"])
            # insert record in the Person table (table of users)
            person_user.insert()
            # login user and remember user
            login_user(person_user, remember=True)
            time.sleep(0.5)
            return {'result' : True}
        except:
            print(sys.exc_info())
            abort(400)


@app.before_first_request
def here():
    print("here")
@app.route("/try" , methods=['POST'])
def trying():
    print(current_user.is_authenticated)
    return "asdjl"

# create route when authorized, a GET request is requested to check if user is authenticated
@app.route("/authorized" , methods=['GET'])
def authorized():
    print(current_user.is_authenticated)
    # is authenticated is method from flask-login
    if(current_user.is_authenticated):
        return {"result" : True}
    else: 
        return {"result" : False}

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

################################# SOCKETS ################################################
# decorater function used so only authenticated users can use sockets
# only logged in users can emit events that will be handled by back end
import functools
def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

############################# CURSOR SOCKET MANAGEMENT ###############################
# socket connection
@socketio.on('connect')
def handle_message():
    # sid is the session id of the user that is connected
    print("client connected " , request.sid)

# socket disconnection
# when client disconnects for reason such as closing the browser
@socketio.on('disconnect')
@authenticated_only
def test_disconnect():
    # each user enters room and we cache which room user is in 
    # once user is disconnected, we use the cache room to find the session ID of user
    room = cachedRooms[request.sid]
    # when client disconnects, client will leave room
    leave_room(room)
    # emit to all other clients in the same room when member is leaving so other clients can remove cursor of member from it'ss si
    emit('member_leaving' , {"sid" : request.sid} , room = room)

def messageReseved():
    print("message sent")


@socketio.on('chat')
@authenticated_only
def handle_message(objectData):
    userID = objectData['userData']['user_id']
    # jwt = objectData['userData']['jwt']
    recepitID = objectData['userData']['communicate']
    print('emitting message')
    emit("send message" , {'message' : objectData['message'] , 'id' : recepitID , 'from' : userID} ,ack = messageReseved , broadcast = True)

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

# socket recieve registerMouse message from client
@socketio.on('registerMouse')
@authenticated_only
def registerMouse(objectData):
    # query the person table to search for user with id of client 
    user =  Person.query.filter_by(id = current_user.id).first()
    # if user exists
    if(user != None):
        data = user.print_self()
        # emit x and y coordinates of mouse, document id, user name, and room
        emit('reciveMouse' , {"x" : objectData['x'] , "y" :objectData['y']  ,"sid" : request.sid,"name" : data['Username'] } ,room = objectData['room'])

# socket recieve leaveGroup message from client
@socketio.on('leaveGroup')
@authenticated_only
def registerMouse(objectData):
    # client leaves room when logged out
    leave_room(objectData['room'])
    user =  Person.query.filter_by(id = current_user.id).first()
    data = user.print_self()
    # emit to client when member is leaving and give the id of the user and the room user is in
    emit('member_leaving' , {"sid" : request.sid} , room = objectData['room'])


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




