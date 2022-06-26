// will contain all the data of the document in db
const {Schema, model} = require('mongoose')

// set up new schema
const Document = new Schema({
    // document is just an id and some data
    _id: String, 
    data: Object
})

// export it as a model and pass it to our schema 
module.exports = model("Document", Document)

// now we have a document in db and can store these info. in db