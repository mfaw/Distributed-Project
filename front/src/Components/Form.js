
import './Form.css';
import React  , {useState , useEffect, Fragment} from 'react'
import axios from 'axios';
import io from 'socket.io-client';
import GridLoader from "react-spinners/GridLoader";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUser } from '@fortawesome/free-solid-svg-icons'
let firstTime = true

// form for signing in to homepage
function Form(props){
    // declare new state variable called formData
    const [formData , setFromData] = useState({
        Email : '',
        UserName : '',
        Password : ''
    })
    // declare new state variable called signIn
    let [signIn , setSignIn] = useState(true);
    // declare new state variable called loading
    let [loading , setLoading] = useState(false);
    // declare new state variable called errorMessage
    const [errorMessage , setErrorMessage] = useState('')
    
    // handler of clicking on button event
    const handleClick = (event)=>{
        event.preventDefault();
        // if username and email are writte and password not empty
        if(formData['UserName'] !== '' && (formData['Email'] !== '' || signIn === true)&& formData['Password'] !== ''){
            setLoading(true)
            // if user is signing in
            if(signIn){
                console.log("jere")
                // passing sign in form data -- post form data
                axios.post('/signin', {
                    'Data': formData,
                  })
                  // response of posting form data
                  .then(function (response) {
                    // if sign in details (== response.data.result) are correct
                      if(response.data.result === true){

                          console.log("hereeeee")
                          // sign in by setting the view of the sign in to false
                          setTimeout(() => {
                              props.setViewSignIn(false)
                          }, 200);

                      }else{
                        // if sign in details are  not correct, give error message
                        setLoading(false)
                        setErrorMessage("username or password are wrong")
                      }
                  })
                  // if form data not posted, catch error and show error message
                  .catch(function (error) {
                    console.log(error)
                    ;
                });
            }else{
                // else user is signing up
                // passing sign up form data -- post form data
                axios.post('/signup', {
                    'Data' : formData
                  })
                  // response of posting form data
                  .then(function (response) {
                    // if sign up details (== response.data.result) are correct 
                    if(response.data.result === true){
                        console.log("here")
                        // sign up by setting the view of the sign in to false
                        setTimeout(() => {
                            props.setViewSignIn(false)
                        }, 200);

                    }else{
                        // if sign up details are  not correct, give error message
                        setLoading(false)
                        setErrorMessage("username or email is already in use")
                    }
                  })
                  // if form data not posted, catch error and show error message
                  .catch(function (error) {
                    console.log(error);
                });
            }
            
        }

    }
    // handling changes in the form
    // a form element initiated an event and triggered the handler function
    const handleFormChane = (event)=>{
        const {name , value} = event.target
        // if there is a change in the form, we set the form data   
        setFromData((prevState) =>{
            return({
                // change the state that maintains the form info to the new state corresponding to the change in the form element
                ...prevState,
                [name] : value
            })
        })
    }

    // login and sign up form
    const fortmView = (
        <>

        <form className="form">
        <FontAwesomeIcon icon={faUser} className="user-icon"/>
        {errorMessage && <p className="errorMessage">{errorMessage}</p>}
        {signIn ? 
            (
                <>
                    /* 2 inputs for sign in, usernme and password */
                    <input
                        name="UserName"
                        className="form-username form-textbox"
                        placeholder="UserName"
                        /* value typed will be the user name in the form data */
                        value={formData.UserName}
                        /** on change initiates and event that triggers handleFormChange */
                        onChange={(event) => handleFormChane(event)}
                        autocomplete="off"
                        type='text'
                    />
                    <input
                        name="Password"
                        className="form-password form-textbox"
                        placeholder="Password"
                        /* value typed will be the user name in the form data */
                        value={formData.Password}
                        /** on change initiates and event that triggers handleFormChange */
                        onChange={(event) => handleFormChane(event)}
                        autocomplete="off"
                        type='password'
                    />
                    /**The login button onclick event triggers the handleClick function */
                    <button
                        onClick={handleClick}
                        className = "login-button"
    
                    >Log in</button>
                </>
            )
        :
            (
                <>
                    /**Sign up is same as login but, 3 inputs (username, password, and email) */
                    <input
                        name="UserName"
                        className="form-username form-textbox"
                        placeholder="UserName"
                        value={formData.UserName}
                        onChange={(event) => handleFormChane(event)}
                        autocomplete="off"
                        type='text'
                    />
                    <input
                        name="Password"
                        className="form-password form-textbox"
                        placeholder="Password"
                        value={formData.Password}
                        onChange={(event) => handleFormChane(event)}
                        autocomplete="off"
                        type='password'
                    />
                    <input
                        name="Email"
                        className="form-email form-textbox"
                        placeholder="Email"
                        value={formData.Email}
                        onChange={(event) => handleFormChane(event)}
                        autocomplete="off"
                        type='email'
                    />
                     
                    <button
                        onClick={handleClick}
                        className = "login-button"

                        /**Button changes to login if it's sign in and sign up otherwise */
                    >{signIn ? 'LOG IN' : 'SIGN UP'}</button>
                </>
            )
        }
        </form>
    </>
    )
    return(
        // returns the grid loader if loding is true -- fetching from server
        // and the forms won't appear
        <div className="form-container">
            <GridLoader color='rgb(6, 6, 98);' loading={loading} size={15} />
            /**If loading is false, data fetched from server done, 
            the form will be viewed and the input toggle switch to go from sign up to sign in and vice versa */
            {!loading && fortmView }
            {!loading && 
            <div className="checkbox--container">
                <p>{signIn? "SIGN IN" : "SIGN UP" }</p>
                <input
                    type="checkbox"
                    id="switch"
                    class="checkbox" 
                    onClick={() => setSignIn(prev => !prev)}
                />
                <label 
                    for="switch"
                    class="toggle"
                />
            </div>
            }

        </div>
    )
}

export default Form;