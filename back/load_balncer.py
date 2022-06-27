
from argparse import Namespace
from asyncio.log import logger
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
SECRETKEY = "mySecretKey"

app = Flask(__name__)
CORS(app)
setup_db(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Documents"
app.debug = True
mongo = PyMongo(app)
login_manager = LoginManager()
login_manager.login_view = 'logoutUseer'
login_manager.init_app(app)

app.config['SECRET_KEY'] = SECRETKEY
socketio = SocketIO(app , logger = False , cors_allowed_origins="*" , async_handlers=False)
# db_drop_and_create_all()

workers = {} # cache all avalibasle worker (worker ker -> value port of the worker)
documentSupporters = {} # cache worker port that supports the already opened document plus number of useres in the room
sessionRoom = {} # Cache ther users the key is sessio id value is the port number handled by the worker 

@login_manager.user_loader
def load_user(user_id):
    return Person.query.get(int(user_id))

@app.route("/logout")
@login_required
def logoutUseer():
    if(current_user.is_authenticated):
        logout_user()
    return {"result" : "loginError"}

@app.route("/signin" , methods=['POST'])
@requires_auth()
def sign_in(instance):
    print(workers ,
documentSupporters ,
sessionRoom )
    if (instance):
        login_user(instance, remember=True)
        data = { 
            "result" : True,
        }
        time.sleep(0.5)
        return data
    else:
        time.sleep(0.5)
        return {'result' : False}

@app.route("/signup" , methods=['POST'])
def sign_up():
    try:
        port = random.choice(list(workers.values()))
        url = f'http://127.0.0.1:{port}/signup'
        response = requests.post(url, json = request.get_json())
        if(response.json()['result'] == False):
            return response.json()
        else:
            user =  Person.query.filter_by(id = response.json()['user']['id']).first()
            login_user(user, remember=True)
            return {'result' : True}

    except: 
        print(sys.exc_info())
        abort(400) 
   




@app.route("/authorized" , methods=['GET'])
def authorized():
    print(current_user.is_authenticated)
    if(current_user.is_authenticated):
        return {"result" : True}
    else: 
        return {"result" : False}



@app.route("/addDocumnet" , methods=['POST'])
@login_required
def addDocument():
    try:
        port = random.choice(list(workers.values()))
        url = f'http://127.0.0.1:{port}/addDocumnet'
        response = requests.post(url, json = request.get_json())
        return response.json()
   
    except :
        return {"result" : "loginError"}



@app.route("/allDocuments" , methods=['GET'])
@login_required
def getAllDocuments():
    try:
        port = random.choice(list(workers.values()))
        url = f'http://127.0.0.1:{port}/allDocuments'
        response = requests.get(url, json = request.get_json())
        return response.json()
   
    except :
        return {"result" : "loginError"}

    


# sockets starts here

import functools
def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

@socketio.on('connect')
@authenticated_only
def handle_message():
    # url = 'http://127.0.0.1:5002/connect'
    # requests.post(url, json = {'sid' : request.sid})
    print(f"{request.sid} is being served by a worker process")

@socketio.on('disconnect')
@authenticated_only
def test_disconnect():
    url = 'http://127.0.0.1:5002/disconnect'
    response = requests.post(url, json = {'sid' : request.sid})
    room = response.json()['room']
    print(f"number of users ----------------> {documentSupporters[room][1]}")
    if(documentSupporters[room][1] <= 1):
        del documentSupporters[room]
    else:
        documentSupporters[room][1]-=1
    if request.sid in sessionRoom:
        del sessionRoom[request.sid]
    print("member is leaving")
    if(room != "None"):
        leave_room(room)
        emit('member_leaving' , {"sid" : request.sid} , room = room)


def registerSupporter(objectData):
    global documentSupporters
    global sessionRoom
    if(objectData['room'] in documentSupporters):
        port = documentSupporters[objectData['room']][0]
        if(request.sid in sessionRoom):
            pass
        else:
            documentSupporters[objectData['room']][1]+=1
    else:
        port = random.choice(list(workers.values()))
        documentSupporters[objectData['room']] = [port , 1]

    sessionRoom[request.sid] = port
    return port

@socketio.on('connectToRoom')
@authenticated_only
def connectToNewRoom(objectData):

    port = registerSupporter(objectData)
    print(f"number of users ----------------> {documentSupporters[objectData['room']][1]}")
    print(documentSupporters)
    url = f'http://127.0.0.1:{port}/connectToRoom'
    response = requests.post(url, json = {'sid' : request.sid , 'room' : objectData['room']})
    join_room(objectData['room'])
    emit('reciveDocument' , {"data" : response.json()['data'] , "sid" : request.sid})


@socketio.on('registerMouse')
@authenticated_only
def registerMouse(objectData):
    if objectData['room'] in documentSupporters: 
        port = documentSupporters[objectData['room']][0]
    else:
        port = registerSupporter(objectData)
    url = f'http://127.0.0.1:{port}/registerMouse'
    response = requests.post(url, json = {'id' : current_user.id})
    user = response.json()['name']

    if(user != "None"):

        emit('reciveMouse' , {"x" : objectData['x'] , "y" :objectData['y']  ,"sid" : request.sid,"name" : user } ,room = objectData['room'])


@socketio.on('leaveGroup')
@authenticated_only
def leaveGroup(objectData):
    leave_room(objectData['room'])
    print(f"number of users ----------------> {documentSupporters[objectData['room']][1]}")
    port = documentSupporters[objectData['room']][0]
    url = f'http://127.0.0.1:{port}/leaveGroup'
    if(documentSupporters[objectData['room']][1] <= 1):
        del documentSupporters[objectData['room']]
    else:
        documentSupporters[objectData['room']][1]-=1
    if request.sid in sessionRoom:
        del sessionRoom[request.sid]
    requests.post(url, json = {'sid' : request.sid})
    emit('member_leaving' , {"sid" : request.sid} , room = objectData['room'])


# here the Quill managemnt for documents
# so when we emit, we emit to document 
# sending changes to specific room
# listen to changes from client 
@socketio.on('send-changes')
@authenticated_only
def send_changes(objectData):
    room = objectData['room']
    delta = objectData['delta']
    # broadcast message to everyone else that there are changes which is delta
    emit('receive-changes' , {"sid" : request.sid , 'delta' : delta} , room = room)



# want to save our document by updating data of document
# takes all our data
# must be called from client
@socketio.on('save-document')
@authenticated_only
def save_document(objectData):
    port = random.choice(list(workers.values()))
    url = f'http://127.0.0.1:{port}/save_document'
    requests.post(url, json = objectData)




@socketio.on('registerport')
def registerport(objectData):
    if(request.sid in workers):
        pass
    else:
        workers[request.sid] = objectData['port']
        print(workers)


# handling the server sockets and requests

NUM_WORK = 0

@app.route("/registerServer" , methods=['POST'])
def registerServer():
    global workers
    global NUM_WORK
    payload = request.get_json()
    workers[f"WORKER_{NUM_WORK}"] = payload['port']
    NUM_WORK+=1
    print(workers)
    return {"result" : True}



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


def checkWorkers():
    global workers
    global documentSupporters
    global sessionRoom
    for key in workers:
        url = f'http://127.0.0.1:{workers[key]}/condition'
        try:
            response = requests.get(url)
        except:

            for key2 in documentSupporters:
                if documentSupporters[key2][0] == workers[key]:
                    del documentSupporters[key2]
                    break
            for key2 in sessionRoom:
                if sessionRoom[key2] == workers[key]:
                    del sessionRoom[key2]
                    break
            
            del workers[key]
            continue
        if(response.json()['result'] != True):
           del workers[key]
            

if __name__ == '__main__':

    scheduler = APScheduler()
    scheduler.add_job(func=checkWorkers, trigger='interval', id='job', seconds=4)
    scheduler.start()

    socketio.run(app , debug = False)



