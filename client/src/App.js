import TextEditor from './TextEditor'
// router to allow handling multiple documents
import {
  BrowserRouter as Router,
  Route, 
  Routes, // switch
  Navigate, //redirect 
} from 'react-router-dom' //v6
import { v4 as uuidV4 } from 'uuid'

function App() {
  // to use a router we will wrap everything inside a router
  // routes aka switch determine our different routes 
  // in each route there is a case on our routes statement on the root path
  // route the homepage exactly and render want to redirect it to random document
  // uuid is a package to generate unique id
  // generating random document to redirect to immediately then back to text editor
  // another route to route any document with id and want to render our text editor
  
  return (
  <Router>
    <Routes>
      <Route path="/" element={<a href={`/documents/${uuidV4()}`}>Create document</a>} />
      <Route path='/documents/:id' element={ <TextEditor />}/>
    </Routes>
  </Router>
    )
}

export default App;

