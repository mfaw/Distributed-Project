
import './App.css';
import React  , {useState , useEffect} from 'react'
import axios from 'axios';
import Cursor from './Components/Cursor'; 
import Form from './Components/Form';
import DocList from './Components/DocList';
import {
  BrowserRouter as Router,
  Routes ,
  Route,
} from "react-router-dom";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {  faRightFromBracket} from '@fortawesome/free-solid-svg-icons'

function App() {
  let [viewForm , setViewForm] = useState(true)
  const setViewSignIn = (value) =>{
    setViewForm(value)
    
  }
  // get authorization, if authorized, then user is logged in so we don't view the form
  // this is allows user to stay logged in when page is refreshed
  useEffect(()=>{
    axios.get('/authorized')
    .then((response)=>{
      if(response.data.result== true) {
        setViewForm(false);
      }
     
    })
  } , [viewForm])
  return (
      <>
      {/* /**Wrapping everything inside a route which is the switch, then we determine the route*/ }
         <Routes>
         {/* /** If view form is false, Route to the list of documents */ }
          {(!viewForm) &&<Route exact path="/" element = {<DocList setViewSignIn = {setViewSignIn}/>}/>}
          {/* /**If view form is true, route to show sign in form */ }
          {(viewForm) && <Route exact path="/" element = {<Form setViewSignIn = {setViewSignIn}  />}/>}
          {/* /** If view form is false, Route to a document with id */ }
          {(!viewForm) && <Route exact path="/document/:id" element = {<Cursor/>}/>}
          {/* /** If view form is false, Route to the list of documents */ }
          {(!viewForm) && <Route exact path="*" element = {<DocList setViewSignIn = {setViewSignIn}/>}/>}
          {/* /**If view form is true, route to show sign in form */ }
          {(viewForm) && <Route exact path="*" element = {<Form setViewSignIn = {setViewSignIn}  />}/>}


          
        </Routes>
        {/* /**If view form is false, view the log out button*/ }
        {(!viewForm) && <div className='logoutbutton-container'>
                <button
                    onClick={()=>{
                      axios.get('/logout')
                      .then((response)=>{
                        if(response.data.result== "loginError") {
                          
                          setViewForm(true);
                        }
                       
                      })
                    }}
                    className='logoutbutton'
                > <FontAwesomeIcon className='logout-icon' icon={faRightFromBracket}/></button>
          </div>}
      </>
     





     

   
  );
}

export default App;
