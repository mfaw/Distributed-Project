const mongoose = require('mongoose')
const Document = require('./Document')

// connect with mongoose to db
mongoose.connect("mongodb://localhost/dist-project")

const QuillCursors = require('quill-cursors')

//import io from socket io which is a function we should run
// pass port we want to run on code, client port: 3000
const io = require('socket.io')(3001, {
    // use cors (cross-origin resource sharing) bc server and client are on different ports
    // cors is a mechanism that allows a server to indicate any origins other than its own from which a browser should permit loading resources
    // this will allow to make request from different url to different url
    cors: {
        //specify origin of client and methods alowed
        origin: 'http://localhost:3000',
        methods: ['GET', 'POST'] 
    }
})

// io object will allow us to do the connections
// every time client connects it will run io connection and give server a socket
// server will use socket to communicate back to client
io.on("connection", socket=>{
    // event sent to client
    // async bc we have to await finding a document
    socket.on('get-document', async documentId => {
        // loads up the data
        const document = await findORcreateDoc(documentId)
        // socket joins a room for the documentId
        // when calling join we are putting socket in a room and everyone in room can talk based on the documentId
        socket.join(documentId)
        // make sure socket emits out correct data
        socket.emit('load-document', document.data)
        // so when we emit, we emit to document 
        // sending changes to specific room
        // listen to changes from client
        socket.on('send-changes', delta => {
        // broadcast message to everyone else that there are changes which is delta
            socket.broadcast.to(documentId).emit('receive-changes', delta)
    })

    // want to save our document by updating data of document
    // takes all our data
    // must be called from client
    socket.on('save-document', async data => {
        await Document.findByIdAndUpdate(documentId, {data})
    })
    })
    
})

const defaultValue = ""
// we either find document or create it from scratch
// async bc we use await
async function findORcreateDoc(id){
    if(id==null) return

    // await trying to find document 
    const document = await Document.findById(id)
    // if we have document, we return to user, if not return creation of new document
    if (document) return document
    // else
    return await Document.create({_id: id, data: defaultValue})

}