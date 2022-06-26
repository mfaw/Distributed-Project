from pymongo import MongoClient
DATABASE = "Documents"

## creating mongodb for the document
client = MongoClient('mongodb://localhost:27017/')
db = client[DATABASE_NAME]