SmartSpendAnalyser

SmartSpendAnalyser is a Python Flask application that automates expense tracking. It processes uploaded receipt images using OCR, intelligently categorizes spending (e.g., Travel, Personal Care, Education) into a MongoDB database, and provides users with clear, categorized financial insights.

Features
User Authentication: Secure user registration and login.

Receipt Upload: Allows users to upload images of their physical receipts.

OCR Integration: Extracts text from receipt images using Optical Character Recognition.

Intelligent Data Parsing: Converts raw extracted text into structured financial data (e.g., total amount, items).

Automated Expense Categorization: Categorizes expenses based on a robust, rule-based system (e.g., identifying "Travel" from keywords like "flight" or "hotel").

Comprehensive Expense History: Stores and retrieves all processed receipts and associated data for historical tracking.

MongoDB Backend: Utilizes a NoSQL database for flexible and scalable data storage.

Technology Stack
Backend: Python 3.x, Flask

Database: MongoDB

Database Driver: PyMongo

Environment Management: python-dotenv

OCR: (Implied, but not explicitly in provided code snippets, typically an external library or API)

Password Hashing: (Implied, but not explicitly in provided code snippets, typically Werkzeug.security or bcrypt)

Setup and Installation
Follow these steps to get the SmartSpendAnalyser backend running on your local machine.

Prerequisites
Python 3.8+: Download and install from python.org.

MongoDB Community Server: Download and install from mongodb.com/try/download/community.

Important: Ensure MongoDB is running and accessible (default port 27017).

MongoDB Shell (mongosh): Install mongosh separately if it's not included with your MongoDB Server installation. Make sure its bin directory is added to your system's PATH environment variable so you can run it from any command prompt. (Refer to MongoDB documentation for detailed PATH setup instructions for your OS).

Installation Steps
Clone the repository:

git clone <https://github.com/Ammu1pillai/SmartSpend.git/>

cd SmartSpendAnalyser/BACKEND_1/app



Create a virtual environment (recommended):

python -m venv venv

Activate the virtual environment:

Windows:

.\venv\Scripts\activate

macOS/Linux:

source venv/bin/activate

Install dependencies:
Create a requirements.txt file in your backend/app directory (if you don't have one) with the following content:

Flask

pymongo

python-dotenv

Flask

Pillow

pytesseract

flask-cors

Flask-Login

Werkzeug

Flask-JWT-Extended

Then install them:

pip install -r requirements.txt

Configure Environment Variables:
Create a file named .env in the backend/app directory and add your MongoDB connection details:

MONGO_URI="mongodb://localhost:27017/"
DB_NAME="SmartSpendDB"


Run the Flask application:

python wsgi.py

You should see output indicating the Flask development server is running, typically on http://127.0.0.1:5000/.

Database Structure
The application uses a MongoDB database named SmartSpendDB (by default) with two primary collections:

Users Collection:

Stores user registration details.

Fields: _id (ObjectId), username (string), password (hashed string), email (string, optional), join_date (datetime).

Receipts Collection:

Stores information extracted from uploaded receipts.

Fields: _id (ObjectId), user_id (ObjectId, linking to the Users collection), image_path (string), extracted_text (string, raw OCR output), parsed_data (document/dict, structured data like total, items, categories), timestamp (datetime).

Expense Categorization Logic
The SmartSpendAnalyser includes a rule-based system for categorizing expenses. This system checks for specific keywords within the item_name_lower (lowercase item name) derived from the parsed receipt data. Examples of categories and their keywords include:

Travel: flight, hotel, airline, train, bus, cab fare, taxi, uber, rental car, accommodation, cruise, airport transfer, toll, parking.

Personal Care: shampoo, soap, body wash, toothpaste, makeup, lotion, perfume, salon, haircut, spa, razor, sunscreen, manicure, pedicure.

Education: tuition, course fee, school fee, textbook, notebook, stationery, online course, workshop, tutoring, student loan.

Gifts & Donations: gift, donation, charity, present, contribute, fundraiser, sponsorship.



Usage (API Endpoints - Example)
Once the server is running, you can interact with it via its API endpoints. (Specific endpoint details would typically be provided in separate API documentation or within the Flask routes).

User Registration: POST /register

User Login: POST /login

Upload Receipt: POST /upload-receipt (with image file)

Get User Receipts: GET /receipts/<user_id>

Demo Video
https://drive.google.com/file/d/1VyOJ1YXEbrDVRzrWJjVdYJhFaiy7bWTd/view?usp=sharing

Collaborators
Pillai Anjita: Frontend Development

Neha M: Backend Development

Catherine Elsa Philipose: API Integration and Data Cleaning
