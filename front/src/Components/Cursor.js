
import './Cursor.css';
import React  , {useState , useEffect, Fragment  , useCallback} from 'react'
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowPointer , faRightFromBracket} from '@fortawesome/free-solid-svg-icons'
import io from 'socket.io-client';
// const SOCKET_URL = "urlasd";
import {
    useParams ,
    useNavigate
  } from "react-router-dom";

// quill is not a react component so, we should make it work with react
import Quill from "quill"
//importing ready stylesheet in quill - theme: snow
import "quill/dist/quill.snow.css"



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

/////////////////////////////////////////////////////Cursor Implementation///////////////////////////
// this function is to show users in a document through their cursor
function Cursor(props) {
    // declare new state variable with documentData, allUsers, and current user
    let [documentData , setDocumentData] = useState(null)
    let [allUsers , setAllUsers] = useState({});
    let [currentUser , setCurrentUser] = useState(null);
    //put socket in a state to be able to access it from any place to allow syncing changes
    const [socket, setSocket] = useState()
    // same goes for quill 
    const [quill, setQuill] = useState()

    const { id } = useParams();
    const navigate = useNavigate();

    // creating new socket and setting it to create the socket connection
    useEffect( ()=>{
        const createSocketConnection = async() =>{
            const newSocket = io();
            setSocket(newSocket);
          }
          if(socket == null){
            createSocketConnection();
          }
    } , [socket])

    useEffect(() =>{

        if(socket != null){
            // listen to event, listen to event once and cleans it up
            // we will get the load-document event from our server
            socket.on('reciveDocument' , (data)=>{
                // want to tell server which document it is
                // if document saved we will send document baack
                // set the document data and current user
                setDocumentData(data['data'])
                setCurrentUser(data['sid'])
                console.log(data['data'])
                socket.off('reciveDocument')
            })
            // emit to connect to room with it's id when client receives document
            // so client will join a room
            // emit to server
            socket.emit('connectToRoom' , {'room' : id});

            console.log("here")
           
        }

      
      },[ socket, currentUser])

    // client leaves room when log out button is clicked
    const leaveRoom = (id)=>{
        document.onmousemove = (event)=>{
        }
        console.log("here" , navigate)
        // if socket is not null, emit the leaveGroup with the room id
        // and navigate user to login page
        if(socket != null) socket.emit('leaveGroup' , {"room" : id})
        if(socket != null) navigate('/');
    }
    useEffect(()=>{
        return ()=>{
            // return leaveRoom
            if(socket != null){
                leaveRoom(id)
            }
        }
    },[socket])

    useEffect(()=>{
        // for each user in all users, get a pointer, background, and username
        for( let curser in allUsers){
            let pointer = document.getElementById('icon-pointer-'+curser)
            let background = document.getElementById('cursor-background-'+curser);
            let username = document.querySelector('#user-info-container-'+curser+' p')

            // show the background color and username when mouse is on cursor
            pointer.addEventListener('mouseenter' , ()=>{
                background.classList.add("view-data");
                username.classList.add("view-data-p");
                console.log(username)
            })
             // remove the background color and username when mouse is not on cursor
            pointer.addEventListener('mouseleave' , ()=>{
                background.classList.remove("view-data");
                username.classList.remove('view-data-p');
            })
        }

        // if connection is open and a user is leaving
        if(socket != null){
            // handler event of socket io
            async function member_leaving(data){
                setAllUsers(prev =>{
                    let updated = {...prev}
                    console.log(updated)
                    // delete the current user that left from all users list
                    delete updated[data['sid']]
                    console.log(updated)
                    // setAllUsers will return the updated users list
                    return updated
                })
             }

            // handler event of socket io
            function controlMessage(data) {
                // if user that moved cursor is already a current user
                if(data['sid'] != currentUser && currentUser!= null){
                    if(allUsers.hasOwnProperty(data['sid'])){
                        setAllUsers(prev => {
                            let updated = {...prev}
                            // update the x and y of the cursor position only
                            updated[data['sid']] = {"name" : data['name'] , "x" : data['x'] , "y" : data['y'] , "color" : updated[data['sid']]['color']}
                            return(
                                updated
                            )
                        })
                    }else{
                        // else, if user is a new user
                        // assign a new color to the user and update x and y position of cursor
                        let randomColor = Math.floor(Math.random()*16777215).toString(16);
                        setAllUsers(prev => {
                            let updated = {...prev}
                            updated[data['sid']] = {"name" : data['name'] , "x" : data['x'] , "y" : data['y'], "color" : randomColor}
                            return(
                                updated
                            )
                        })
                    }
                }
            }

            // window.addEventListener('beforeunload', handleTabClose);
            // listen for member leaving or receiving mouse event
            socket.on('member_leaving' , member_leaving)
            // mouse event is when user moves mouse in the document
            socket.on('reciveMouse' , controlMessage) 
            return ()=>{
            // window.removeEventListener('beforeunload', handleTabClose);
            // unbind the handler
            socket.off('member_leaving' ,member_leaving)
            socket.off('reciveMouse' , controlMessage)
        }
 
        }
      
    } , [socket , allUsers , currentUser])


    const myfunction = async()=>{
        if(socket != null){
            let old_position = [0 , 0]
            let dim = [window.innerWidth , window.innerHeight]
            // event triggered when mouse moves to emit new mouse positions to server
            document.onmousemove = (event)=>{
                let pos = [event.clientX , event.clientY]
                if(Math.abs(pos[0] - old_position[0]) + Math.abs(pos[1] - old_position[1]) > 100){
                    // emits to socket to register position of mouse, x and y, and the room it belongs to
                    socket.emit('registerMouse' , {'x' : pos[0]/dim[0] , 'y' : pos[1]/dim[1] , 'room' : id})
                    old_position[0] = pos[0]
                    old_position[1] = pos[1]
                    
                }
            }
        }
    }
    myfunction();

    let cursers = []
    let dim = [window.innerWidth , window.innerHeight]
    // loop over all users (cursors) available and create for each  the divs below
    // these create the cursor, cursor container and background depending on the data from the x and y coordinates
    // each cursor has a unique id and key to control the mouse when it moves on the screen
    for(let curser in allUsers){
        cursers.push(
            <div className='ex' id={'ex-'+curser} style={{top: dim[1] * allUsers[curser]['y'] , left: dim[0] * allUsers[curser]['x']  }} >
                <div className='cursor-container' id={'cursor-container-' + curser} key = {'cursor-container-' + curser}>
                    <div className='cursor-background' style = {{backgroundColor: '#'+allUsers[curser]['color']}} id={'cursor-background-'+curser}  key =  {'cursor-background-'+curser} >
                    </div>                
                    <div className='user-info-container' id={'user-info-container-'+curser} key = {'user-info-container-'+curser} >
                        <FontAwesomeIcon icon={faArrowPointer} color={"#"+allUsers[curser]['color']} className="icon-pointer" id={'icon-pointer-' + curser} key = {'icon-pointer-' + curser}></FontAwesomeIcon>
                        <p key={"nameUser-"+curser}>{allUsers[curser]['name']}</p> 
                    </div>
                </div>
            </div>
        )
    }

/////////////////////////////////////////////////////Quill Implementation///////////////////////////

    useEffect(() => {
        if(socket == null || quill == null) return
            //set the content of the document 
            if(documentData != null){
               quill.setContents(documentData);
            }

            // we disable text editor until document is loaded and then enable it
            quill.enable()
  
    }, [socket , documentData, quill]) //depends on socket, quill, document id

    // to save document 
    useEffect(() => {
        // check if socket and quill exist
        if (socket == null || quill == null) return

        // set up timer to save every interval
        const interval = setInterval(() =>{
            // save document by getting contents of text editor
            if(documentData != null){
                socket.emit('save-document', {'data' : quill.getContents() , 'name' : id})
            }

        }, SAVEINTERVAL_MS) // every .. we save document
        return() => {
            // clear interval so it won't run anymore
            clearInterval(interval)
        }
    }, [socket, quill , documentData])

     // handler to receive event -- same as sending changes
     useEffect(() => {
        if (socket == null || quill == null) return
        // delta we get from our received changes
        const handler = (data) => {
            // run changes, delta, on code to make these changes
            if(data['sid'] != currentUser && currentUser != null){
                quill.updateContents(data['delta'])

            }

        }
        // instead quill emitting changes, socket will receive changes from the server
        socket.on('receive-changes', handler)
        return () => {
            socket.off('receive-changes', handler)
        }
    }, [socket, quill , currentUser])
    // detect changes whenever quill changes
    // send changes to the server
    // server will listen to the changes 

    useEffect(() => {
        // make sure we have a socket and quill
        // setting up event listener
        if (socket == null || quill == null || currentUser == null) return
        // text-change is an API event in quill
        // source shows who made these changes, user or not, as we track user changes only
        // const cache = [];
        const handler = async (delta, oldDelta, source) => {
            if(source!== 'user') return // if changes were made by API for example, we don't want to do anything
            // we don't want to send chanages to the server to the other client unless changes were made by the user
            // send changes to server by emitting message from client to server
            // we send delta which is the only thing that schanged, not the whole document
            // cache.push(delta)
            // let old = oldDelta['ops']
            // let newDel = quill.getContents()['ops']
            // let DifferentOps = []
            // for (let i = 0 ; i < old.length;i++){
            //     condiiton = false
            //     for (let key in old[i]){
            //         if (old[i][key] == newDel[i][key]) continue;
            //         DifferentOps.push(newDel[i])
            //         break;
            //     }   
            // }
            
     
          
            await new Promise(resolve =>{
                socket.emit('send-changes', {'delta' : delta , 'room' : id} , (answer)=>{
                    resolve(answer);
                })
            })
            
        }
        quill.on('text-change', handler)
        //remove event listener if no longer needed
        return () => {
            quill.off('text-change', handler)
        }
    }, [socket, quill , currentUser]) //this function relies on socket and quill
    
    const wrapperRef = useCallback((wrapper) => {
        if (wrapper == null) return
        // every time we call function make sure wrapper is empty - clean up
        wrapper.innerHTML = ''
        //create new elements
        const editor = document.createElement('div');
        // put editor inside the wrapper 
        wrapper.append(editor);
        // new to create new instance that takes a selector which is the id(quill being instantiated in editor object) and the snow theme 
        const q = new Quill(editor, {theme: "snow", modules: {toolbar: toolbar}})
        // quill is disabled
        q.disable()
        q.setText('Loading...')
        setQuill(q);
    }, []) // [] : render first time component mounts
    // as we change the code and save, new toolbars are created with different div
    // so, we want to wrap all toolbars in one container to remove it all when useEffect ends clean up
    // solution -> put editor inside this container by ref to reference it
    return (
        <Fragment>
             <div className="container" ref={wrapperRef}></div>
            {cursers}
            <div className='logoutbutton-container'>
                /**When log out button is clicked it initiates and event to trigger leaveRoom function*/
                <button
                    onClick={ () => props.leaveRoom(id)}
                    className='logoutbutton'
                > <FontAwesomeIcon className='logout-icon' icon={faRightFromBracket}/></button>
            </div>
        </Fragment>
  
            
     
           
    
    )

}

export default Cursor;