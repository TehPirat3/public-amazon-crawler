"""
Created MongoDB document to store item's detailed information
"""
import pymongo
import settings

connection = pymongo.MongoClient(
            host = settings.MONGODB_SERVER,
            port = settings.MONGODB_PORT
        )

db = connection[settings.MONGODB_DB]

products = db['products']
