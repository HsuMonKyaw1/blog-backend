from pymongo import MongoClient

# MongoDB Atlas connection string
mongo_uri = "mongodb+srv://hsumonk001:hsumonkyaw12345@cluster0.nzi4wje.mongodb.net/?retryWrites=true&w=majority"

# Create a MongoDB client
client = MongoClient(mongo_uri)

# Access your database
db = client.social_platform
