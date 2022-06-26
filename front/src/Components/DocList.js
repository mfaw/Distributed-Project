
import './DocList.css';
import React  , {useState , useEffect, Fragment} from 'react'
import axios from 'axios';
import io from 'socket.io-client';
import GridLoader from "react-spinners/GridLoader";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUser } from '@fortawesome/free-solid-svg-icons'
import Cursor from './Cursor';

import {
    BrowserRouter as Router,
    Switch,
    Route,
    Link,
    useNavigate,
} from "react-router-dom";



export default function DocList(props){
    // declare new state variable called documentName
    let [documentName , setDocumentName] = useState('');
    // declare new state variable called errorMessage
    let [errorMessage , setErrorMessage] = useState('');
    // declare new state variable called documentList
    let [documentList , setDocumentList] = useState([]);

    const navigate = useNavigate();
    // handling changes in the form
    // a form element initiated an event and triggered the handler function
    const handleFormChane = (event)=>{
        const {value} = event.target
        setDocumentName((prevState) =>{
            return(value)
        })
    }

    // must be logged in to view the documents list
    const checkLogin = (response)=>{
        if(response.data.result == 'loginError'){
            props.setViewSignIn(true)
        }
    }
    // when create button is clicked, handleClick is triggered
    const handleClick = (e)=>{
        e.preventDefault();
        // passing the document name to add document -- post
        axios.post('/addDocumnet', {
            'Data': documentName,
          })
          // if posted
          .then(function (response) {
            // check user is logged in
              checkLogin(response)
              // if document name is creted in db
              if(response.data.result === 'created'){
                setErrorMessage('')
                // get all documents and show them in document list as response
                axios.get('/allDocuments')
                    .then((response)=>{
                        checkLogin(response)    
                        setDocumentList(response.data.result)
                    })
                    // else give error message if document name already exists
              }else if(response.data.result === 'documentNameError'){
                setErrorMessage("Document already created")
              }
            
            })
    }
    // get all documents and show them in list
    useEffect(()=>{
        axios.get('/allDocuments')
        .then((response)=>{        
            setDocumentList(response.data.result)
        })
    

    } , [])

    const handleDocumentClick = (e)=>{
        // event which navigates the document folder with the id of the element
            navigate('/document/'+e.target.id)
    }
    // document elements returns the list of the documents by mapping the element and index
    const documentElements = documentList.map((element , index) =>{
        return(
            <>
            /**onclick triggers the handleDocumentClick event which navigates the document folder with the id of the element
            to return a list of documents*/
            <div className='document-contianer' onClick={handleDocumentClick} id = {element.name} key = {'doc'+index}>
                <p className='document'>{element.name}</p>
            </div>
            <hr/>
            </>
        )
    })

    return (
        // returns a list of documents and input box with create button
        <div className='document-list-container'>
            {errorMessage && <p className='errorMessage'>{errorMessage}</p>}
            /** list of documents returned */
            <div className='document-list'>
                {documentElements}

            </div>
            <div className='add-new-document'>
                /**input box to type in document name and click create */
                <input
                name="documentName"
                className="form-textbox-document"
                placeholder="Document Name"
                /**document name typed in initiates an event that triggers handleFormChange function */
                value={documentName}
                onChange={(event) => handleFormChane(event)}
                autocomplete="off"
                type='text'
                />
                /**create button that initiates an event when clicked and triggers the handleclick function */
                <button
                        onClick={handleClick}
                        className = "add-document-button"
                >Create</button>
            </div>
        </div>
        
       
    )
}



