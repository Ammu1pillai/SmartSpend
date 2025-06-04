# SmartSpendAnalyser/backend/app/database.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
db_name = os.getenv("DB_NAME", "SmartSpendDB")

client = None
db = None
receipts_collection = None
users_collection = None

def initialize_db():
    """
    Initializes the MongoDB connection and sets up global client and collection objects.
    This function should be called once when the Flask app starts.
    """
    global client, db, receipts_collection, users_collection
    try:
        client = MongoClient(mongo_uri)
        # The 'ping' command is good for verifying connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        db = client[db_name]
        receipts_collection = db["Receipts"]
        users_collection = db["Users"]
    except Exception as e:
        print(f"Could not connect to MongoDB: {e}")
        # In a real app, you might want more robust error handling,
        # like logging or raising a specific exception.

# Optionally, call initialize_db() here if you want it to connect immediately on module import.
# However, for Flask, it's often better to call it within create_app().
# For this structure, we'll call it in __init__.py.