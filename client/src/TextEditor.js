import {useEffect, useState, useCallback} from 'react'
// quill is not a react component so, we should make it work with react
import Quill from "quill"
//importing ready stylesheet in quill - theme: snow
import "quill/dist/quill.snow.css"
// to allow client to make a connection
import {io} from 'socket.io-client'
// to get document id
import { useParams } from 'react-router-dom'
import QuillCursors from "quill-cursors"

// Register QuillCursors module to add ability to show multiple cursors on the editor.
Quill.register('modules/cursors', QuillCursors);

// Constant to simulate a high-latency connection when sending cursor
// position updates.
const CURSOR_LATENCY = 1000;

// Constant to simulate a high-latency connection when sending
// text changes.
const TEXT_LATENCY = 500;

const SAVEINTERVAL_MS = 2000 // 2 seconds
//extra toolbar options for the text editor
const toolbar = [
    [{ "font": [] }, { "size": ["small", false, "large", "huge"] }], // custom dropdown

    ["bold", "italic", "underline", "strike"],

    [{ "color": [] }, { "background": [] }],

    [{ "script": "sub" }, { "script": "super" }],

    [{ "header": 1 }, { "header": 2 }, "blockquote", "code-block"],

    [{ "list": "ordered" }, { "list": "bullet" }, { "indent": "-1" }, { "indent": "+1" }],

    [{ "direction": "rtl" }, { "align": [] }],

    ["link", "image", "video", "formula"],

    ["clean"]
]

export default function TextEditor() {
    const {id: documentId} = useParams()
    console.log(documentId)
    //put socket in a state to be able to access it from any place to allow syncing changes
    const [socket, setSocket] = useState()
    // same goes for quill 
    const [quill, setQuill] = useState()
    // want client to connect to server once 
    // returns a socket to server
    useEffect(() => {
        // connect socket to server port
        const s = io("http://localhost:3001")
        //setting socket
        setSocket(s)
        // when we are done we clean up by disconnecting the socket from the server
        return () => {
            s.disconnect()
        }
    }, [])
    useEffect(() => {
        if(socket == null || quill == null) return
        // listen to event, listen to event once and cleans it up
        // we will get the load-document event from our server
        socket.once("load-document", document => {
            //send back to client
            quill.setContents(document)
            // we disable text editor until document is loaded and then enable it
            quill.enable()
        })
        // want to tell server which document it is
        // if document saved we will send document baack
        socket.emit('get-document', documentId)

    }, [socket, quill, documentId]) //depends on socket, quill, document id
    // to save document 
    useEffect(() => {
        // check if socket and quill exist
        if (socket == null || quill == null) return

        // set up timer to save every interval
        const interval = setInterval(() =>{
            // save document by getting contents of text editor
            socket.emit('save-document', quill.getContents())
        }, SAVEINTERVAL_MS) // every .. we save document
        return() => {
            // clear interval so it won't run anymore
            clearInterval(interval)
        }
    }, [socket, quill])
    console.log(socket)
    // handler to receive event -- same as sending changes
    useEffect(() => {
        if (socket == null || quill == null) return
        // delta we get from our received changes
        const handler = (delta) => {
            // run changes, delta, on code to make these changes
            quill.updateContents(delta)
        }
        // instead quill emitting changes, socket will receive changes from the server
        socket.on('receive-changes', handler)
        return () => {
            socket.off('receive-changes', handler)
        }
    }, [socket, quill])
    // detect changes whenever quill changes
    // send changes to the server
    // server will listen to the changes 
    useEffect(() => {
        // make sure we have a socket and quill
        // setting up event listener
        if (socket == null || quill == null) return
        // text-change is an API event in quill
        // source shows who made these changes, user or not, as we track user changes only
        const handler = (delta, oldDelta, source) => {
            if(source!== 'user') return // if changes were made by API for example, we don't want to do anything
            // we don't want to send chanages to the server to the other client unless changes were made by the user
            // send changes to server by emitting message from client to server
            // we send delta which is the only thing that changed, not the whole document
            socket.emit('send-changes', delta)
            setTimeout(() => quill.updateContents(delta), TEXT_LATENCY);
            
            console.log(delta)
        }
        quill.on('text-change', handler)
        //remove event listener if no longer needed
        return () => {
            quill.off('text-change', handler)
        }
    }, [socket, quill]) //this function relies on socket and quill
    //create new instance of quill
    //useEffect: used to do something once when we render the page -- therefore, must import useEffect
    // replaced with useCallback later to avoid problem of calling useEffect before wrapper
    const wrapperRef = useCallback((wrapper) => {
        if (wrapper == null) return
        // every time we call function make sure wrapper is empty - clean up
        wrapper.innerHTML = ''
        //create new elements
        const editor = document.createElement('div');
        // put editor inside the wrapper 
        wrapper.append(editor);
        // new to create new instance that takes a selector which is the id(quill being instantiated in editor object) and the snow theme 
        const q = new Quill(editor, {theme: "snow", modules: {cursors: {transformOnTextChange: true}, toolbar: toolbar}})
        // quill is disabled
        const cursorsOne = q.getModule('cursors')
        cursorsOne.createCursor('cursor', 'User 2', 'blue');
        q.disable()
        q.setText('Loading...')
        setQuill(q);
    }, []) // [] : render first time component mounts
    
    // as we change the code and save, new toolbars are created with different div
    // so, we want to wrap all toolbars in one container to remove it all when useEffect ends clean up
    // solution -> put editor inside this container by ref to reference it
  return <div className="container" ref={wrapperRef}></div>
}