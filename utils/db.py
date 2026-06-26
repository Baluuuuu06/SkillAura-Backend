from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI)
# Get database name from the URI (e.g. lpd_db)
db_name = Config.MONGO_URI.split('/')[-1].split('?')[0]
db = client[db_name]
