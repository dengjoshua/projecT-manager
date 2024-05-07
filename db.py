from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = 'mongodb://localhost:27017'
client = AsyncIOMotorClient(MONGO_DETAILS)
database_name = "project_handler"
database = client[database_name]
collection_name = "users" 
db = database[collection_name]