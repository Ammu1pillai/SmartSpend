# SmartSpendAnalyser/backend/app/db.py
import datetime
from bson.objectid import ObjectId
import uuid 

# Import the actual database objects from the database connection module
# This breaks the circular dependency with __init__.py
from .database import client, db, receipts_collection, users_collection


def insert_receipt_to_db(user_id, image_path, extracted_text, parsed_data=None):
    """
    Inserts a new receipt document into the 'Receipts' collection.
    Args:
        user_id (str): The ID of the user associated with the receipt.
        image_path (str): The file path where the receipt image is stored.
        extracted_text (str): The text extracted from the receipt image.
        parsed_data (dict, optional): Dictionary of structured data from OCR (e.g., total, items).
    Returns:
        str: The ID of the inserted receipt document if successful, None otherwise.
    """
    # Ensure collections are initialized before use
    if client is None or receipts_collection is None:
        print("Cannot insert receipt: MongoDB client or receipts_collection is not initialized.")
        return None
    
    try:
        user_object_id = ObjectId(user_id)
    except Exception as e:
        print(f"Invalid user_id '{user_id}' provided for receipt insertion: {e}")
        return None
    
    receipt_doc = {
        "user_id": user_object_id,
        "image_path": image_path,
        "extracted_text": extracted_text,
        "parsed_data": parsed_data if parsed_data is not None else {}, 
        "timestamp": datetime.datetime.utcnow()
    }
    try:
        result = receipts_collection.insert_one(receipt_doc)
        print(f"Receipt inserted with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error inserting receipt: {e}")
        return None

def find_user_by_username(username):
    """
    Finds a user by their username in the 'Users' collection.
    """
    if client is None or users_collection is None:
        print("Cannot find user: MongoDB client or users_collection is not initialized.")
        return None
    try:
        user = users_collection.find_one({"username": username})
        return user
    except Exception as e:
        print(f"Error finding user by username '{username}': {e}")
        return None

def find_user_by_id(user_id):
    """
    Finds a user by their ObjectId in the 'Users' collection.
    """
    if client is None or users_collection is None:
        print("Cannot find user by ID: MongoDB client or users_collection is not initialized.")
        return None
    try:
        if not ObjectId.is_valid(user_id):
            print(f"Invalid ObjectId string for user_id in find_user_by_id: {user_id}")
            return None
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        return user
    except Exception as e:
        print(f"Error finding user by ID '{user_id}': {e}")
        return None


def create_user(username, hashed_password, email=None):
    """
    Creates a new user in the 'Users' collection.
    """
    if client is None or users_collection is None:
        print("Cannot create user: MongoDB client or users_collection is not initialized.")
        return None
    try:
        if find_user_by_username(username):
            print(f"User with username '{username}' already exists.")
            return None

        user_doc = {
            "username": username,
            "password": hashed_password,
            "email": email,
            "join_date": datetime.datetime.utcnow()
        }
        result = users_collection.insert_one(user_doc)
        print(f"User '{username}' created with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error creating user '{username}': {e}")
        return None

def get_user_receipts(user_id):
    """
    Fetches all receipts associated with a specific user ID from the 'Receipts' collection.
    """
    if client is None or receipts_collection is None:
        print("Cannot fetch receipts: MongoDB client or receipts_collection is not initialized.")
        return []
    try:
        if not ObjectId.is_valid(user_id):
            print(f"Invalid ObjectId string for user_id in get_user_receipts: {user_id}")
            return []
          
        receipts = list(receipts_collection.find({"user_id": ObjectId(user_id)}).sort("timestamp", -1))
        for receipt in receipts:
            # Convert ObjectId to string for consistent JSON serialization
            receipt['_id'] = str(receipt['_id']) 
            if 'user_id' in receipt: 
                receipt['user_id'] = str(receipt['user_id'])
            if 'timestamp' in receipt and isinstance(receipt['timestamp'], datetime.datetime):
                receipt['timestamp'] = receipt['timestamp'].isoformat() # Convert to ISO format string
        return receipts
    except Exception as e:
        print(f"Error fetching receipts for user {user_id}: {e}")
        return []

# Example usage (for testing this file independently)
if __name__ == "__main__":
    print("\n--- Testing db.py functions ---")
    # For independent testing, ensure database.py is imported and initialized first
    from .database import initialize_db, client # Import initialize_db and client for closing
    initialize_db() # Manually initialize DB for standalone test
    
    test_username = f"demouser_{uuid.uuid4().hex[:8]}" 
    test_user_id = create_user(test_username, "test_hashed_password", "demo@example.com")
    if test_user_id:
        print(f"Created demo user with ID: {test_user_id}")
        insert_receipt_to_db(test_user_id, "/dummy/path/img1.jpg", "Test receipt 1", {"total_amount": 15.00, "category": "food"})
        insert_receipt_to_db(test_user_id, "/dummy/path/img2.jpg", "Test receipt 2", {"total_amount": 25.50, "category": "transport"})
        receipts = get_user_receipts(test_user_id)
        print(f"Receipts for demo user: {len(receipts)}")
        for r in receipts:
            print(f"   - ID: {r['_id']}, User ID: {r['user_id']}, Text: {r['extracted_text']}, Parsed: {r['parsed_data']}")
        
        found_user = find_user_by_id(test_user_id)
        if found_user:
            print(f"Found user by ID: {found_user['username']}")
        else:
            print(f"Could not find user by ID: {test_user_id}")

    else:
        print("Demo user not created.")

    if client: # Close the client if it was initialized for the test
        client.close()
        print("\nMongoDB connection closed.")