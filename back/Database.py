from pymongo import MongoClient
DATABASE = "Documents"


client = MongoClient('mongodb://localhost:27017/')
db = client[DATABASE_NAME]