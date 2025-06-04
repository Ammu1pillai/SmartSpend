from flask import request, jsonify, Blueprint, current_app
from PIL import Image
import pytesseract
import os
import uuid
from datetime import datetime, timedelta
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import re # Ensure re is imported

pytesseract.tesseract_cmd = r'C:\Users\pilla\SmartSpend\SmartSpendAnalyser\tessaract_installed\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\Users\pilla\SmartSpend\SmartSpendAnalyser\tessaract_installed\tessdata'

# Import specific functions and collections from db.py
from .db import (
    users_collection,
    receipts_collection,
    find_user_by_username,
    find_user_by_id,
    insert_receipt_to_db,
    get_user_receipts
)
from .ocr_utils import extract_text_from_image

# Create a Blueprint for your routes
main = Blueprint('main', __name__)

# --- CONFIGURATION: Store-Category Mapping ---
# This dictionary maps cleaned merchant names to their primary category
# and optionally provides special item categorization rules if needed.
STORE_CATEGORY_MAP = {
    "mcdonalds": {"overall": "Food & Dining", "items_default": "Food & Dining"},
    "starbucks": {"overall": "Food & Dining", "items_default": "Food & Dining"},
    "kfc": {"overall": "Food & Dining", "items_default": "Food & Dining"},
    "dominos": {"overall": "Food & Dining", "items_default": "Food & Dining"},
    "pizza hut": {"overall": "Food & Dining", "items_default": "Food & Dining"},
    "subway": {"overall": "Food & Dining", "items_default": "Food & Dining"},
    "swiggy": {"overall": "Food & Dining", "items_default": "Food & Dining"},
    "zomato": {"overall": "Food & Dining", "items_default": "Food & Dining"},
    "paradise biryani": {"overall": "Food & Dining", "items_default": "Food & Dining"},
    "haldirams": {"overall": "Food & Dining", "items_default": "Food & Dining"},
    "barbeque nation": {"overall": "Food & Dining", "items_default": "Food & Dining"},

    "big bazaar": {"overall": "Grocery/Supermarket", "items_default": None}, # None means item rules apply
    "dmart": {"overall": "Grocery/Supermarket", "items_default": None},
    "reliance fresh": {"overall": "Grocery/Supermarket", "items_default": None},
    "more retail": {"overall": "Grocery/Supermarket", "items_default": None},
    "spar": {"overall": "Grocery/Supermarket", "items_default": None},
    "walmart": {"overall": "Grocery/Supermarket", "items_default": None}, # Corrected for your example
    "star bazaar": {"overall": "Grocery/Supermarket", "items_default": None},
    "natures basket": {"overall": "Grocery/Supermarket", "items_default": None},
    "easyday": {"overall": "Grocery/Supermarket", "items_default": None},

    "croma": {"overall": "Electronics", "items_default": "Electronics"},
    "reliance digital": {"overall": "Electronics", "items_default": "Electronics"},
    "amazon": {"overall": "Online Shopping", "items_default": None}, # Amazon sells everything, so rely on item keywords
    "flipkart": {"overall": "Online Shopping", "items_default": None},

    "zara": {"overall": "Clothing/Apparel", "items_default": "Clothing/Apparel"},
    "h&m": {"overall": "Clothing/Apparel", "items_default": "Clothing/Apparel"},
    "lifestyle": {"overall": "Clothing/Apparel", "items_default": "Clothing/Apparel"},
    "shoppers stop": {"overall": "Clothing/Apparel", "items_default": "Clothing/Apparel"},
    "myntra": {"overall": "Online Shopping", "items_default": "Clothing/Apparel"}, # Myntra is mainly clothes

    "hpcl": {"overall": "Transportation/Fuel", "items_default": "Transportation/Fuel"},
    "bpcl": {"overall": "Transportation/Fuel", "items_default": "Transportation/Fuel"},
    "indian oil": {"overall": "Transportation/Fuel", "items_default": "Transportation/Fuel"},
    "uber": {"overall": "Transportation/Fuel", "items_default": "Transportation/Fuel"},
    "ola": {"overall": "Transportation/Fuel", "items_default": "Transportation/Fuel"},

    "apollo pharmacy": {"overall": "Healthcare/Pharmacy", "items_default": "Healthcare/Pharmacy"},
    "netmeds": {"overall": "Healthcare/Pharmacy", "items_default": "Healthcare/Pharmacy"},
    "chemist warehouse": {"overall": "Healthcare/Pharmacy", "items_default": "Healthcare/Pharmacy"},
    "medplus": {"overall": "Healthcare/Pharmacy", "items_default": "Healthcare/Pharmacy"},

    "ikea": {"overall": "Household", "items_default": "Household"},
    "home centre": {"overall": "Household", "items_default": "Household"},
    "pepperfry": {"overall": "Household", "items_default": "Household"},

    "pvr": {"overall": "Entertainment", "items_default": "Entertainment"},
    "inox": {"overall": "Entertainment", "items_default": "Entertainment"},
    "bookmyshow": {"overall": "Entertainment", "items_default": "Entertainment"},

    # Generic categories for less specific merchants or general keywords
    "hotel": {"overall": "Travel", "items_default": "Travel"},
    "airlines": {"overall": "Travel", "items_default": "Travel"},
    "flight": {"overall": "Travel", "items_default": "Travel"},
    "bus": {"overall": "Travel", "items_default": "Travel"},
    "railways": {"overall": "Travel", "items_default": "Travel"},
    "stationery": {"overall": "Education", "items_default": "Education"},
    "book store": {"overall": "Education", "items_default": "Education"},
    "spa": {"overall": "Personal Care", "items_default": "Personal Care"},
    "salon": {"overall": "Personal Care", "items_default": "Personal Care"},
    "gym": {"overall": "Health & Fitness", "items_default": "Health & Fitness"},
    "fitness": {"overall": "Health & Fitness", "items_default": "Health & Fitness"},
}

# --- UTILITY FUNCTIONS ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def clean_merchant_name(merchant_name):
    """ Cleans and normalizes merchant names for mapping. """
    return re.sub(r'[^a-z0-9\s]', '', merchant_name.lower()).strip()

def categorize_overall_bill(merchant_name, whole_text):
    """
    Determines the primary category of the entire bill based on merchant name and context.
    """
    merchant_lower = clean_merchant_name(merchant_name)
    whole_text_lower = whole_text.lower()

    # Check direct merchant mapping first
    for store_name, config in STORE_CATEGORY_MAP.items():
        if store_name in merchant_lower: # Use 'in' for partial matches, e.g., "WAL*MART" -> "walmart"
            return config['overall']

    # Fallback to keywords in the overall text if no direct merchant match
    if "restaurant" in whole_text_lower or "cafe" in whole_text_lower or "coffee" in whole_text_lower or "dine" in whole_text_lower:
        return "Food & Dining"
    if "fuel" in whole_text_lower or "petrol" in whole_text_lower or "diesel" in whole_text_lower:
        return "Transportation/Fuel"
    if "pharmacy" in whole_text_lower or "chemist" in whole_text_lower or "medicine" in whole_text_lower:
        return "Healthcare/Pharmacy"
    if "electronics" in whole_text_lower or "gadget" in whole_text_lower or "tv" in whole_text_lower:
        return "Electronics"
    if "fashion" in whole_text_lower or "apparel" in whole_text_lower or "clothing" in whole_text_lower:
        return "Clothing/Apparel"
    if "movie" in whole_text_lower or "cinema" in whole_text_lower or "entertainment" in whole_text_lower:
        return "Entertainment"
    if "bill" in whole_text_lower or "utility" in whole_text_lower:
        return "Bills/Utilities"
    if "hotel" in whole_text_lower or "flight" in whole_text_lower or "travel" in whole_text_lower:
        return "Travel"
    if "school" in whole_text_lower or "college" in whole_text_lower or "tuition" in whole_text_lower:
        return "Education"
    if "salon" in whole_text_lower or "spa" in whole_text_lower or "personal care" in whole_text_lower:
        return "Personal Care"
    if "hardware" in whole_text_lower or "tools" in whole_text_lower:
        return "Tools/Hardware"
    if "home" in whole_text_lower or "furniture" in whole_text_lower or "decor" in whole_text_lower:
        return "Household"

    return "General" # Default if nothing specific is found

def categorize_item(item_name, merchant_category, whole_text):
    """
    Categorizes a single item, considering the overall merchant category.
    """
    item_name_lower = item_name.lower()
    whole_text_lower = whole_text.lower() # For broader context checks

    # 1. If merchant has a specific item default, use it (e.g., McDonald's -> Food & Dining)
    merchant_config = None
    for store_name, config in STORE_CATEGORY_MAP.items():
        if store_name in clean_merchant_name(merchant_category): # Re-use clean merchant name if passed directly from bill
            merchant_config = config
            break

    if merchant_config and merchant_config.get("items_default"):
        # Check for specific exclusions if the default is very broad (e.g., "Non-Spend Item")
        if any(keyword in item_name_lower for keyword in ["discount", "tax", "subtotal", "total", "cash", "change", "amount", "card"]):
            return "Non-Spend Item"
        return merchant_config["items_default"]

    # 2. If no specific merchant default, apply general item-level rules
    # This part gets executed for stores like Big Bazaar, Amazon where items need individual classification.

    # Rule 0: Exclusions for OCR artifacts or non-spend items
    if any(keyword in item_name_lower for keyword in ["discount", "tax", "subtotal", "total", "cash", "change", "amount", "card", "round off"]):
        return "Non-Spend Item"
    if re.search(r'^\d+\.\d{2}$', item_name_lower): # If item name is just a price (OCR error)
        return "Non-Spend Item"


    # Rule 1: Grocery specific items
    if  "milk" in item_name_lower or \
        "bread" in item_name_lower or \
        "eggs" in item_name_lower or \
        "vegetable" in item_name_lower or \
        "fruit" in item_name_lower or \
        "banana" in item_name_lower or \
        "apple" in item_name_lower or \
         "mango" in item_name_lower or \
        "grape" in item_name_lower or \
        "orange" in item_name_lower or \
        "papaya" in item_name_lower or \
        "pineapple" in item_name_lower or \
        "watermelon" in item_name_lower or \
        "pomegranate" in item_name_lower or \
        "lemon" in item_name_lower or \
        "potato" in item_name_lower or \
        "tomato" in item_name_lower or \
        "onion" in item_name_lower or \
        "carrot" in item_name_lower or \
        "beans" in item_name_lower or \
        "cabbage" in item_name_lower or \
        "cauliflower" in item_name_lower or \
        "brinjal" in item_name_lower or \
        "ladyfinger" in item_name_lower or \
        "okra" in item_name_lower or \
        "cucumber" in item_name_lower or \
        "spinach" in item_name_lower or \
        "beetroot" in item_name_lower or \
        "pumpkin" in item_name_lower or \
        "garlic" in item_name_lower or \
        "ginger" in item_name_lower or \
        "green chili" in item_name_lower or \
        "red chili" in item_name_lower or \
        "capsicum" in item_name_lower or \
        "radish" in item_name_lower or \
        "turnip" in item_name_lower or \
        "spring onion" in item_name_lower or \
        "peas" in item_name_lower or \
        "broccoli" in item_name_lower or \
        "mushroom" in item_name_lower or \
        "sweet corn" in item_name_lower or \
        "zucchini" in item_name_lower or \
        "drumstick" in item_name_lower or \
        "bitter gourd" in item_name_lower or \
        "bottle gourd" in item_name_lower or \
        "ridge gourd" in item_name_lower or \
        "ash gourd" in item_name_lower or \
        "tinda" in item_name_lower or \
        "turmeric" in item_name_lower or \
        "haldi" in item_name_lower or \
        "chili powder" in item_name_lower or \
        "masala" in item_name_lower or \
        "spice" in item_name_lower or \
        "salt" in item_name_lower or \
        "sugar" in item_name_lower or \
        "jaggery" in item_name_lower or \
        "oil" in item_name_lower or \
        "ghee" in item_name_lower or \
        "rice" in item_name_lower or \
        "basmati" in item_name_lower or \
        "brown rice" in item_name_lower or \
        "dal" in item_name_lower or \
        "lentil" in item_name_lower or \
        "chana" in item_name_lower or \
        "moong" in item_name_lower or \
        "toor" in item_name_lower or \
        "urad" in item_name_lower or \
        "rajma" in item_name_lower or \
        "soya" in item_name_lower or \
        "poha" in item_name_lower or \
        "flattened rice" in item_name_lower or \
        "suji" in item_name_lower or \
        "rava" in item_name_lower or \
        "maida" in item_name_lower or \
        "wheat" in item_name_lower or \
        "atta" in item_name_lower or \
        "flour" in item_name_lower or \
        "corn flour" in item_name_lower or \
        "bajra" in item_name_lower or \
        "jowar" in item_name_lower or \
        "barley" in item_name_lower or \
        "millet" in item_name_lower or \
        "quinoa" in item_name_lower or \
        "oats" in item_name_lower or \
        "biscuit" in item_name_lower or \
        "snack" in item_name_lower or \
        "namkeen" in item_name_lower or \
        "juice" in item_name_lower or \
        "water bottle" in item_name_lower or \
        "tea" in item_name_lower or \
        "coffee" in item_name_lower or \
        "pickle" in item_name_lower or \
        "jam" in item_name_lower or \
        "sprout" in item_name_lower or \
        "mung bean" in item_name_lower or \
        "black chana" in item_name_lower or \
        "white chana" in item_name_lower or \
        "green gram" in item_name_lower or \
        "kidney bean" in item_name_lower or \
        "mustard" in item_name_lower or \
        "fennel" in item_name_lower or \
        "fenugreek" in item_name_lower or \
        "ajwain" in item_name_lower or \
        "hing" in item_name_lower or \
        "jeera" in item_name_lower:
        return "Grocery"



    # Rule 2: Food & Dining (general)
    if "burger" in item_name_lower or \
        "pizza" in item_name_lower or \
        "coffee" in item_name_lower or \
        "tea" in item_name_lower or \
        "chai" in item_name_lower or \
        "latte" in item_name_lower or \
        "cappuccino" in item_name_lower or \
        "espresso" in item_name_lower or \
        "sandwich" in item_name_lower or \
        "sub" in item_name_lower or \
        "wrap" in item_name_lower or \
        "shawarma" in item_name_lower or \
        "roll" in item_name_lower or \
        "fries" in item_name_lower or \
        "french fries" in item_name_lower or \
        "nuggets" in item_name_lower or \
        "taco" in item_name_lower or \
        "nachos" in item_name_lower or \
        "meal" in item_name_lower or \
        "combo" in item_name_lower or \
        "thali" in item_name_lower or \
        "curry" in item_name_lower or \
        "biryani" in item_name_lower or \
        "rice" in item_name_lower or \
        "noodles" in item_name_lower or \
        "pasta" in item_name_lower or \
        "maggi" in item_name_lower or \
        "paratha" in item_name_lower or \
        "roti" in item_name_lower or \
        "naan" in item_name_lower or \
        "paneer" in item_name_lower or \
        "chicken" in item_name_lower or \
        "mutton" in item_name_lower or \
        "fish" in item_name_lower or \
        "egg" in item_name_lower or \
        "dal" in item_name_lower or \
        "sabji" in item_name_lower or \
        "veg" in item_name_lower or \
        "nonveg" in item_name_lower or \
        "buffet" in item_name_lower or \
        "lunch" in item_name_lower or \
        "dinner" in item_name_lower or \
        "breakfast" in item_name_lower or \
        "snack" in item_name_lower or \
        "chaat" in item_name_lower or \
        "pani puri" in item_name_lower or \
        "samosa" in item_name_lower or \
        "vada" in item_name_lower or \
        "idli" in item_name_lower or \
        "dosa" in item_name_lower or \
        "uttapam" in item_name_lower or \
        "poha" in item_name_lower or \
        "upma" in item_name_lower or \
        "kichdi" in item_name_lower or \
        "dessert" in item_name_lower or \
        "ice cream" in item_name_lower or \
        "kulfi" in item_name_lower or \
        "sweet" in item_name_lower or \
        "cake" in item_name_lower or \
        "pastry" in item_name_lower or \
        "brownie" in item_name_lower or \
        "cookie" in item_name_lower or \
        "donut" in item_name_lower or \
        "chocolate" in item_name_lower or \
        "juice" in item_name_lower or \
        "shake" in item_name_lower or \
        "smoothie" in item_name_lower or \
        "lassi" in item_name_lower or \
        "buttermilk" in item_name_lower or \
        "soda" in item_name_lower or \
        "drink" in item_name_lower or \
        "frap" in item_name_lower:
        return "Food & Dining"

    # Rule 3: Transportation / Fuel
    if "fuel" in item_name_lower or \
       "petrol" in item_name_lower or \
       "diesel" in item_name_lower or \
       "gas" in item_name_lower or \
       "fare" in item_name_lower or \
       "cab" in item_name_lower or \
       "ticket" in item_name_lower and ("bus" in item_name_lower or "train" in item_name_lower or "metro" in item_name_lower):
        return "Transportation"

    # Rule 4: Household / Home Goods
    if "cleaner" in item_name_lower or \
    "detergent" in item_name_lower or \
    ("soap" in item_name_lower and "personal" not in item_name_lower) or \
    "utensil" in item_name_lower or \
    "plate" in item_name_lower or \
    "glass" in item_name_lower or \
    "spoon" in item_name_lower or \
    "fork" in item_name_lower or \
    "knife" in item_name_lower or \
    "bowl" in item_name_lower or \
    "tray" in item_name_lower or \
    "mug" in item_name_lower or \
    "jug" in item_name_lower or \
    "bottle" in item_name_lower or \
    "bucket" in item_name_lower or \
    "mop" in item_name_lower or \
    "broom" in item_name_lower or \
    "dustbin" in item_name_lower or \
    "furniture" in item_name_lower or \
    "sofa" in item_name_lower or \
    "chair" in item_name_lower or \
    "table" in item_name_lower or \
    "bed" in item_name_lower or \
    "mattress" in item_name_lower or \
    "pillow" in item_name_lower or \
    "curtain" in item_name_lower or \
    "lamp" in item_name_lower or \
    "light" in item_name_lower or \
    "bulb" in item_name_lower or \
    "fan" in item_name_lower or \
    "decor" in item_name_lower or \
    "vase" in item_name_lower or \
    "photo frame" in item_name_lower or \
    "wall art" in item_name_lower or \
    "towel" in item_name_lower or \
    "bedsheet" in item_name_lower or \
    "blanket" in item_name_lower or \
    "doormat" in item_name_lower or \
    "floor mat" in item_name_lower or \
    "air freshener" in item_name_lower or \
    "insect repellent" in item_name_lower:
        return "Household"

    # Rule: Tools / Hardware
    if "hammer" in item_name_lower or \
    "drill" in item_name_lower or \
    "screwdriver" in item_name_lower or \
    "wrench" in item_name_lower or \
    "pliers" in item_name_lower or \
    "spanner" in item_name_lower or \
    "screw" in item_name_lower or \
    "nut" in item_name_lower or \
    "bolt" in item_name_lower or \
    "nail" in item_name_lower or \
    "tape" in item_name_lower or \
    "saw" in item_name_lower or \
    "cutter" in item_name_lower or \
    "blade" in item_name_lower or \
    "tool" in item_name_lower or \
    "toolkit" in item_name_lower or \
    "paint" in item_name_lower or \
    "brush" in item_name_lower or \
    "roller" in item_name_lower or \
    "sandpaper" in item_name_lower or \
    "chisel" in item_name_lower or \
    "measuring tape" in item_name_lower or \
    "level" in item_name_lower or \
    "welding" in item_name_lower or \
    "adhesive" in item_name_lower or \
    "fevicol" in item_name_lower or \
    "sealant" in item_name_lower or \
    "putty" in item_name_lower or \
    "hardware" in item_name_lower:
        return "Tools/Hardware"


    # Rule 6: Healthcare / Pharmacy
    if "medicine" in item_name_lower or \
    "pill" in item_name_lower or \
    "tablet" in item_name_lower or \
    "capsule" in item_name_lower or \
    "syrup" in item_name_lower or \
    "ointment" in item_name_lower or \
    "gel" in item_name_lower or \
    "cream" in item_name_lower or \
    "injection" in item_name_lower or \
    "vaccine" in item_name_lower or \
    "bandage" in item_name_lower or \
    "band-aid" in item_name_lower or \
    "gauze" in item_name_lower or \
    "cotton" in item_name_lower or \
    "antiseptic" in item_name_lower or \
    "disinfectant" in item_name_lower or \
    "sanitizer" in item_name_lower or \
    "mask" in item_name_lower or \
    "glove" in item_name_lower or \
    "thermometer" in item_name_lower or \
    "bp monitor" in item_name_lower or \
    "blood pressure" in item_name_lower or \
    "oximeter" in item_name_lower or \
    "inhaler" in item_name_lower or \
    "nebulizer" in item_name_lower or \
    "first aid" in item_name_lower or \
    "painkiller" in item_name_lower or \
    "paracetamol" in item_name_lower or \
    "ibuprofen" in item_name_lower or \
    "antacid" in item_name_lower or \
    "allergy" in item_name_lower or \
    "diabetic" in item_name_lower or \
    "insulin" in item_name_lower or \
    "multivitamin" in item_name_lower or \
    "supplement" in item_name_lower:
        return "Healthcare"


    # Rule 7: Electronics
    if "phone" in item_name_lower or \
    "mobile" in item_name_lower or \
    "smartphone" in item_name_lower or \
    "charger" in item_name_lower or \
    "power bank" in item_name_lower or \
    "laptop" in item_name_lower or \
    "notebook" in item_name_lower or \
    "tablet" in item_name_lower or \
    "ipad" in item_name_lower or \
    "computer" in item_name_lower or \
    "desktop" in item_name_lower or \
    "monitor" in item_name_lower or \
    "keyboard" in item_name_lower or \
    "mouse" in item_name_lower or \
    "printer" in item_name_lower or \
    "scanner" in item_name_lower or \
    "router" in item_name_lower or \
    "modem" in item_name_lower or \
    "headphones" in item_name_lower or \
    "earphones" in item_name_lower or \
    "earbuds" in item_name_lower or \
    "airpods" in item_name_lower or \
    "tv" in item_name_lower or \
    "television" in item_name_lower or \
    "speaker" in item_name_lower or \
    "soundbar" in item_name_lower or \
    "bluetooth" in item_name_lower or \
    "smartwatch" in item_name_lower or \
    "fitness band" in item_name_lower or \
    "battery" in item_name_lower or \
    "adapter" in item_name_lower or \
    "usb" in item_name_lower or \
    "cable" in item_name_lower or \
    "memory card" in item_name_lower or \
    "pen drive" in item_name_lower or \
    "hard disk" in item_name_lower or \
    "ssd" in item_name_lower or \
    "webcam" in item_name_lower or \
    "mic" in item_name_lower or \
    "microphone" in item_name_lower or \
    "projector" in item_name_lower:
        return "Electronics"


    # Rule 8: Clothing / Apparel
    if "shirt" in item_name_lower or \
    "t-shirt" in item_name_lower or \
    "pant" in item_name_lower or \
    "jeans" in item_name_lower or \
    "trouser" in item_name_lower or \
    "shorts" in item_name_lower or \
    "jacket" in item_name_lower or \
    "coat" in item_name_lower or \
    "blazer" in item_name_lower or \
    "sweater" in item_name_lower or \
    "hoodie" in item_name_lower or \
    "kurta" in item_name_lower or \
    "kurti" in item_name_lower or \
    "saree" in item_name_lower or \
    "salwar" in item_name_lower or \
    "lehenga" in item_name_lower or \
    "churidar" in item_name_lower or \
    "dupatta" in item_name_lower or \
    "dress" in item_name_lower or \
    "gown" in item_name_lower or \
    "skirt" in item_name_lower or \
    "top" in item_name_lower or \
    "blouse" in item_name_lower or \
    "innerwear" in item_name_lower or \
    "lingerie" in item_name_lower or \
    "bra" in item_name_lower or \
    "underwear" in item_name_lower or \
    "nightwear" in item_name_lower or \
    "nightdress" in item_name_lower or \
    "pyjama" in item_name_lower or \
    "pajama" in item_name_lower or \
    "vest" in item_name_lower or \
    "socks" in item_name_lower or \
    "shoe" in item_name_lower or \
    "slipper" in item_name_lower or \
    "sandals" in item_name_lower or \
    "sneaker" in item_name_lower or \
    "boot" in item_name_lower or \
    "cap" in item_name_lower or \
    "hat" in item_name_lower or \
    "scarf" in item_name_lower or \
    "glove" in item_name_lower or \
    "belt" in item_name_lower or \
    "tie" in item_name_lower or \
    "uniform" in item_name_lower:
        return "Clothing/Apparel"


    # Rule 9: Entertainment
    if "movie ticket" in item_name_lower or \
    "cinema" in item_name_lower or \
    "game" in item_name_lower or \
    "concert" in item_name_lower or \
    "show" in item_name_lower or \
    "theatre" in item_name_lower or \
    "netflix" in item_name_lower or \
    "amazon prime" in item_name_lower or \
    "disney+" in item_name_lower or \
    "hotstar" in item_name_lower or \
    "zee5" in item_name_lower or \
    "book" in item_name_lower and "notebook" not in item_name_lower and "textbook" not in item_name_lower and "account book" not in item_name_lower or \
    "subscription" in item_name_lower and ("netflix" in item_name_lower or "prime" in item_name_lower or "hotstar" in item_name_lower or "ott" in item_name_lower):
        return "Entertainment"

    # Rule 10: Bills / Utilities (items that would be on a bill, e.g. "internet plan")
    if "electricity" in item_name_lower or \
    "power bill" in item_name_lower or \
    "water bill" in item_name_lower or \
    "sewage" in item_name_lower or \
    "gas bill" in item_name_lower or \
    "lpg" in item_name_lower or \
    "internet" in item_name_lower or \
    "broadband" in item_name_lower or \
    "wifi" in item_name_lower or \
    "recharge" in item_name_lower and ("mobile" in item_name_lower or "data" in item_name_lower) or \
    "phone bill" in item_name_lower or \
    "mobile bill" in item_name_lower or \
    "postpaid" in item_name_lower or \
    "prepaid" in item_name_lower or \
    "plan" in item_name_lower and ("mobile" in item_name_lower or "data" in item_name_lower or "internet" in item_name_lower) or \
    "utility bill" in item_name_lower:
        return "Bills/Utilities"


    # Rule 11: Travel (e.g., if a hotel bill lists "room service")
    if "flight" in item_name_lower or \
       "hotel" in item_name_lower or \
       "airline" in item_name_lower or \
       "airfare" in item_name_lower or \
       "train" in item_name_lower or \
       "bus" in item_name_lower or \
       "cab fare" in item_name_lower or \
       "taxi" in item_name_lower or \
       "uber" in item_name_lower or \
       "ola" in item_name_lower or \
       "lyft" in item_name_lower or \
       "rental car" in item_name_lower or \
       "car rental" in item_name_lower or \
       "accommodation" in item_name_lower or \
       "lodging" in item_name_lower or \
       "motel" in item_name_lower or \
       "guesthouse" in item_name_lower or \
       "hostel" in item_name_lower or \
       "resort" in item_name_lower or \
       "vacation rental" in item_name_lower or \
       "cruise" in item_name_lower or \
       "travel insurance" in item_name_lower or \
       "baggage fee" in item_name_lower or \
       "airport transfer" in item_name_lower or \
       "toll" in item_name_lower or \
       "parking" in item_name_lower:
        return "Travel"

    # Rule 12: Personal Care
    if "shampoo" in item_name_lower or \
       "soap" in item_name_lower or \
       "body wash" in item_name_lower or \
       "conditioner" in item_name_lower or \
       "toothpaste" in item_name_lower or \
       "toothbrush" in item_name_lower or \
       "floss" in item_name_lower or \
       "mouthwash" in item_name_lower or \
       "deodorant" in item_name_lower or \
       "antiperspirant" in item_name_lower or \
       "cosmetics" in item_name_lower or \
       "makeup" in item_name_lower or \
       "lotion" in item_name_lower or \
       "cream" in item_name_lower or \
       "moisturizer" in item_name_lower or \
       "serum" in item_name_lower or \
       "perfume" in item_name_lower or \
       "cologne" in item_name_lower or \
       "razor" in item_name_lower or \
       "shaving cream" in item_name_lower or \
       "aftershave" in item_name_lower or \
       "haircut" in item_name_lower or \
       "hair dye" in item_name_lower or \
       "nail polish" in item_name_lower or \
       "manicure" in item_name_lower or \
       "pedicure" in item_name_lower or \
       "facial" in item_name_lower or \
       "spa" in item_name_lower or \
       "salon" in item_name_lower or \
       "barber" in item_name_lower or \
       "waxing" in item_name_lower or \
       "epilator" in item_name_lower or \
       "sunscreen" in item_name_lower or \
       "hand sanitizer" in item_name_lower or \
       "contact lens solution" in item_name_lower or \
       "eyelash" in item_name_lower or \
       "mascara" in item_name_lower or \
       "lipstick" in item_name_lower or \
       "eyeliner" in item_name_lower or \
       "blush" in item_name_lower or \
       "powder" in item_name_lower or \
       "cotton pads" in item_name_lower or \
       "q-tips" in item_name_lower or \
       "sanitary napkins" in item_name_lower or \
       "tampons" in item_name_lower or \
       "mouth freshner" in item_name_lower:
        return "Personal Care"
    

    # Rule 13: Education
    if "tuition" in item_name_lower or \
       "course fee" in item_name_lower or \
       "school fee" in item_name_lower or \
       "college fee" in item_name_lower or \
       "university fee" in item_name_lower or \
       "admission fee" in item_name_lower or \
       "exam fee" in item_name_lower or \
       "textbook" in item_name_lower or \
       "notebook" in item_name_lower or \
       "stationery" in item_name_lower or \
       "pen" in item_name_lower or \
       "pencil" in item_name_lower or \
       "eraser" in item_name_lower or \
       "ruler" in item_name_lower or \
       "calculator" in item_name_lower or \
       "backpack" in item_name_lower or \
       "school supplies" in item_name_lower or \
       "study guide" in item_name_lower or \
       "online course" in item_name_lower or \
       "e-learning" in item_name_lower or \
       "workshop fee" in item_name_lower or \
       "seminar fee" in item_name_lower or \
       "training program" in item_name_lower or \
       "educational software" in item_name_lower or \
       "library fee" in item_name_lower or \
       "student loan" in item_name_lower or \
       "school trip" in item_name_lower or \
       "extracurricular" in item_name_lower or \
       "coaching" in item_name_lower or \
       "tutoring" in item_name_lower:
        return "Education"

    # Rule 14: Gifts & Donations
    if "gift" in item_name_lower or \
       "donation" in item_name_lower or \
       "charity" in item_name_lower or \
       "present" in item_name_lower or \
       "contribute" in item_name_lower or \
       "fundraiser" in item_name_lower or \
       "sponsorship" in item_name_lower or \
       "tithe" in item_name_lower or \
       "offering" in item_name_lower:
        return "Gifts & Donations"
    
    
    # Default category if no specific rule matches for items
    return merchant_category # Fallback to the overall merchant category if no specific item rule applies


def parse_extracted_text(text):
    """
    This function parses extracted text to find total amount, merchant, date,
    and individual items with their categories.
    """
    total = 0.0
    merchant = "Unknown Merchant"
    transaction_date = datetime.utcnow().isoformat().split('T')[0] # Default to today
    items = []

    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # 1. Improved Total Amount Extraction (prioritize explicitly labeled totals)
    total_match = re.search(r'(?:total|amount|sum|grand total|net amount|bill amount)[:\s]*[A-Z]?\s*(\d+[,.]\d{2})', text, re.IGNORECASE)
    if not total_match:
        total_match = re.search(r'(?:cash received|paid|balance due)[:\s]*[A-Z]?\s*(\d+[,.]\d{2})', text, re.IGNORECASE)
    if not total_match: # If no explicit total label, try finding the largest numeric amount
        all_money_amounts = re.findall(r'\b\d+[,.]\d{2}\b', text)
        if all_money_amounts:
            try:
                # Replace comma with dot for float conversion
                numeric_amounts = [float(a.replace(',', '.')) for a in all_money_amounts]
                # Filter out values that are likely quantities or very small prices
                potential_totals = [a for a in numeric_amounts if a > 0.5] # Heuristic: total usually > 0.5
                if potential_totals:
                    total = max(potential_totals) # Often the largest amount is the total
            except ValueError:
                pass

    if total_match:
        try:
            total = float(total_match.group(1).replace(',', '.'))
        except ValueError:
            pass

    # 2. Improved Merchant Extraction (Prioritize common placements)
    merchant_candidates = []
    # Check first few lines rigorously
    for i, line in enumerate(lines[:6]):
        line_lower = line.lower()
        # Exclude lines that are clearly dates, times, amounts, or common receipt headers/footers
        if not re.search(r'\d{2,4}[-/\.]\d{2}[-/\.]\d{2,4}', line) and \
           not re.search(r'\d{1,2}:\d{2}', line) and \
           not re.search(r'\d+\.\d{2}', line) and \
           not re.search(r'^(gstin|tax|bill|receipt|invoice|total|subtotal|cash|change|thank you|visit again|phone|tel|email|www\.)', line_lower) and \
           len(line.strip()) > 3 and len(line.strip()) < 50: # Reasonable length for a merchant name
            merchant_candidates.append(line.strip())

    if merchant_candidates:
        # Prioritize lines that contain common merchant words or are within the first few lines
        # This is heuristic, can be refined based on more examples
        best_merchant = None
        for candidate in merchant_candidates:
            if "pvt ltd" in candidate.lower() or "store" in candidate.lower() or "supermarket" in candidate.lower() or \
               "cafe" in candidate.lower() or "restaurant" in candidate.lower() or \
               "pharmacy" in candidate.lower() or "mart" in candidate.lower():
                best_merchant = candidate
                break
        if not best_merchant and len(merchant_candidates) > 0:
            best_merchant = merchant_candidates[0] # Fallback to first candidate

        merchant = best_merchant if best_merchant else "Unknown Merchant"
        # Special handling for "WAL*MART" -> "Walmart"
        if "wal*mart" in text.lower() or "wal mart" in text.lower():
            merchant = "Walmart"


    # Determine overall bill category FIRST based on the determined merchant
    overall_category = categorize_overall_bill(merchant, text)


    # 3. Improved Date Extraction
    # Look for common date formats
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
        r'(\d{2}/\d{2}/\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
        r'(\d{2}-\d{2}-\d{4})',  # DD-MM-YYYY or MM-DD-YYYY
        r'(\d{2}/\d{2}/\d{2})',  # DD/MM/YY or MM/DD/YY
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})', # DD Mon YYYY
        r'(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})' # Flexible d.m.y or d/m/y
    ]
    for pattern in date_patterns:
        date_match = re.search(pattern, text)
        if date_match:
            date_str = date_match.group(0)
            try:
                # Attempt to parse common formats
                if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                    transaction_date = datetime.strptime(date_str, '%Y-%m-%d').isoformat().split('T')[0]
                elif re.match(r'\d{2}/\d{2}/\d{4}', date_str): # Try both DMY and MDY
                    try: # DMY first
                        transaction_date = datetime.strptime(date_str, '%d/%m/%Y').isoformat().split('T')[0]
                    except ValueError: # Then MDY
                        transaction_date = datetime.strptime(date_str, '%m/%d/%Y').isoformat().split('T')[0]
                elif re.match(r'\d{2}-\d{2}-\d{4}', date_str): # Try both DMY and MDY
                    try: # DMY first
                        transaction_date = datetime.strptime(date_str, '%d-%m-%Y').isoformat().split('T')[0]
                    except ValueError: # Then MDY
                        transaction_date = datetime.strptime(date_str, '%m-%d-%Y').isoformat().split('T')[0]
                elif re.match(r'\d{2}/\d{2}/\d{2}', date_str):
                    day, month, year = map(int, date_str.split('/'))
                    full_year = 2000 + year if year < 100 else year # Assume 20xx for YY
                    transaction_date = datetime(full_year, month, day).isoformat().split('T')[0]
                elif re.match(r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', date_str, re.IGNORECASE):
                    transaction_date = datetime.strptime(date_str, '%d %b %Y').isoformat().split('T')[0]
                elif re.match(r'\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}', date_str): # Generic d.m.y or d/m/y
                    parts = re.split(r'[-/.]', date_str)
                    if len(parts) == 3:
                        try:
                            # Try DD/MM/YYYY or DD.MM.YYYY
                            transaction_date = datetime(int(parts[2]), int(parts[1]), int(parts[0])).isoformat().split('T')[0]
                        except ValueError:
                            try:
                                # Try MM/DD/YYYY or MM.DD.YYYY
                                transaction_date = datetime(int(parts[2]), int(parts[0]), int(parts[1])).isoformat().split('T')[0]
                            except ValueError:
                                pass
                break # Found and parsed a date, exit loop
            except ValueError:
                pass # Continue to next pattern if parsing fails

    # 4. Item Extraction and Categorization (More Robust with overall_category)
    # Flexible pattern: looks for descriptive text, then optional numbers/codes, then price.
    # It tries to be less strict about what comes before the price.
    # Pattern 1: Item Name with optional quantity/code/tax flags, then price at end of line
    # Added optional currency symbols like $ or Rs.
    item_pattern_1 = re.compile(r'(.+?)(?:\s+\d[\d\s]*[A-Z]?)?\s*(?:[Rs\$€¥£]\s*)?(\d+[,.]\d{2})(?:\s+[NRTX])?\s*$', re.IGNORECASE)

    # Cleaned lines for item parsing
    cleaned_lines = []
    for line in lines:
        line_lower = line.lower()
        # Filter out lines that are clearly not items (e.g., store info, payment details, contact info)
        if any(keyword in line_lower for keyword in ["total", "subtotal", "tax", "gst", "cgst", "sgst", "cash", "change", "balance", "amount", "card", "round off", "thank you", "manager", "open 24 hours", "phone", "tel", "email", "www."]):
            continue
        # Also filter out lines that are just dates, times, or very short/long numbers
        if re.match(r'^\d{2,4}[-/\.]\d{2}[-/\.]\d{2,4}$', line) or \
           re.match(r'^\d{1,2}:\d{2}$', line) or \
           re.match(r'^\d+([,.]\d{2})?$', line) or \
           len(line.strip()) < 3 or len(line.strip()) > 70: # filter out very short/long non-descriptive lines
            continue
        cleaned_lines.append(line)

    for i, line in enumerate(cleaned_lines):
        match = item_pattern_1.search(line)
        if match:
            item_name = match.group(1).strip()
            try:
                item_price = float(match.group(2).replace(',', '.'))
                # Only add if price is positive and item name is not empty
                if item_price > 0.01 and item_name:
                    item_category = categorize_item(item_name, overall_category, text)
                    if item_category != "Non-Spend Item": # Exclude non-spend items during item parsing
                        items.append({"name": item_name, "price": item_price, "category": item_category})
            except ValueError:
                pass # Skip if price conversion fails

    # Fallback for items if none were parsed specifically but a total exists
    # And if the current items sum is significantly less than the total
    current_items_sum = sum(item['price'] for item in items)
    if total > 0 and abs(total - current_items_sum) > 0.5: # If discrepancy is more than 0.5 unit
        remaining_amount = total - current_items_sum
        if remaining_amount > 0.01: # Only add if there's a significant positive remainder
             items.append({"name": "Uncategorized Remainder", "price": remaining_amount, "category": overall_category})
    elif not items and total > 0: # If no items at all, and a total exists, add a generic item
        items.append({"name": "Misc. Purchase", "price": total, "category": overall_category})


    return {
        "total_amount": total,
        "merchant": merchant,
        "date": transaction_date,
        "category": overall_category, # This is the overall bill category
        "items": items, # These are the categorized individual items
        "original_text": text
    }


# === AUTHENTICATION ROUTES ===

@main.route('/register', methods=['POST'])
@cross_origin(supports_credentials=True, origins=["http://localhost:3000"])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not password or not email:
        return jsonify({"msg": "Missing username, email, or password"}), 400

    hashed_password = generate_password_hash(password)

    # Check if username or email already exists
    if users_collection.find_one({"username": username}):
        return jsonify({"msg": "Username already exists"}), 409
    if users_collection.find_one({"email": email}):
        return jsonify({"msg": "Email already registered"}), 409

    user_id = users_collection.insert_one({
        "username": username,
        "email": email,
        "password": hashed_password,
        "join_date": datetime.utcnow()
    }).inserted_id

    return jsonify({
        "msg": "User registered successfully",
        "user_id": str(user_id)
    }), 201

@main.route('/login', methods=['POST'])
@cross_origin(supports_credentials=True, origins=["http://localhost:3000"])
def login():
    print("\n--- BACKEND LOGIN ATTEMPT ---")
    print(f"Request Headers: {request.headers}")
    print(f"Request JSON Data: {request.json}")

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    print(f"Received Username: '{username}'")
    print(f"Received Password (length): {len(password) if password else 0}")
    if not username or not password:
        print("Login Error: Missing username or password in payload.")
        return jsonify({"msg": "Missing username or password"}), 400

    user_data = find_user_by_username(username)

    if not user_data:
        print(f"Login Error: User '{username}' not found in database.")
        return jsonify({"msg": "Invalid username or password"}), 401

    print(f"User found in DB: '{user_data['username']}'")
    print(f"Stored Hashed Password (first 10 chars): '{user_data['password'][:10]}...'")

    password_check_result = check_password_hash(user_data['password'], password)
    print(f"Password Hash Check Result: {password_check_result}")

    if user_data and check_password_hash(user_data['password'], password):
        access_token = create_access_token(identity=str(user_data['_id']))
        return jsonify(
            msg="Login successful",
            access_token=access_token,
            user={
                "id": str(user_data['_id']),
                "username": user_data['username'],
                "email": user_data.get('email')
            }
        ), 200
    else:
        return jsonify({"msg": "Invalid username or password"}), 401

@main.route('/logout', methods=['POST'])
@cross_origin(supports_credentials=True, origins=["http://localhost:3000"])
@jwt_required()
def logout():
    return jsonify({"msg": "Logged out successfully"}), 200

@main.route('/status', methods=['GET'])
@jwt_required()
def status():
    current_user_id = get_jwt_identity()
    user_data = find_user_by_id(current_user_id)

    if user_data:
        return jsonify(
            isLoggedIn=True,
            user={
                "id": str(user_data['_id']),
                "username": user_data['username'],
                "email": user_data.get('email')
            }
        ), 200
    return jsonify({"isLoggedIn": False, "msg": "User not found or token invalid"}), 401


# === PROTECTED ROUTES ===

@main.route('/upload', methods=['POST'])
@cross_origin(supports_credentials=True, origins=["http://localhost:3000"])
@jwt_required()
def upload_receipt():
    current_user_id = get_jwt_identity()

    if 'image' not in request.files:
        return jsonify({'error': 'No image file part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]

        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, unique_filename)
        file.save(filepath)

        try:
            extracted_text = extract_text_from_image(filepath)
            print(f"--- OCR Extracted Text for {unique_filename} ---")
            print(extracted_text)
            print("---------------------------------------")

            parsed_data = parse_extracted_text(extracted_text)
            print(f"--- Parsed Data for {unique_filename} ---")
            print(parsed_data)
            print("-----------------------------------")
            receipt_id = insert_receipt_to_db(current_user_id, filepath, extracted_text, parsed_data)

            if os.path.exists(filepath):
                os.remove(filepath)

            if receipt_id:
                return jsonify({
                    'message': 'Receipt uploaded and processed successfully!',
                    'extracted_text': extracted_text,
                    'parsed_data': parsed_data,
                    'receipt_id': receipt_id
                }), 200
            else:
                return jsonify({'error': 'Failed to save receipt data to database.'}), 500

        except pytesseract.TesseractNotFoundError:
            print("ERROR: Tesseract is not installed or not in PATH.")
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': 'Tesseract OCR engine not found. Please install it.'}), 500
        except Exception as e:
            print(f"OCR or Database Error for {unique_filename}: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Processing failed: {str(e)}'}), 500
    return jsonify({'error': 'Upload failed - no file or empty filename.'}), 500


@main.route('/profile/<user_id>', methods=['GET'])
@cross_origin(supports_credentials=True, origins=["http://localhost:3000"])
@jwt_required()
def get_user_profile(user_id):
    current_user_id = get_jwt_identity()

    if current_user_id != user_id:
        return jsonify({"msg": "Unauthorized access to profile"}), 403

    user = find_user_by_id(user_id)

    if user:
        join_date_str = user["join_date"].isoformat() if isinstance(user.get("join_date"), datetime) else None

        user_data = {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user.get('email', 'N/A'),
            "join_date": join_date_str,
            "totalSpent": 0.0
        }
        user_receipts = get_user_receipts(current_user_id)
        total_spent = sum(r['parsed_data'].get('total_amount', 0) for r in user_receipts if r['parsed_data'])
        user_data['totalSpent'] = total_spent

        return jsonify(user_data), 200
    else:
        return jsonify({"msg": "User not found"}), 404

@main.route('/transactions', methods=['GET'])
@cross_origin(supports_credentials=True, origins=["http://localhost:3000"])
@jwt_required()
def get_transactions():
    current_user_id = get_jwt_identity()
    user_receipts = get_user_receipts(current_user_id)

    transactions = []
    for receipt in user_receipts:
        parsed_data = receipt.get('parsed_data', {})
        transaction_items = []
        if 'items' in parsed_data:
            for item in parsed_data['items']:
                transaction_items.append({
                    "name": item.get('name', 'N/A'),
                    "price": item.get('price', 0.0),
                    "category": item.get('category', 'Uncategorized')
                })

        receipt_date_from_parsed_data = parsed_data.get('date')
        if receipt_date_from_parsed_data:
            date_to_use = receipt_date_from_parsed_data
        elif isinstance(receipt.get('timestamp'), datetime):
            date_to_use = receipt['timestamp'].isoformat().split('T')[0]
        else:
            date_to_use = datetime.utcnow().isoformat().split('T')[0]


        transactions.append({
            "id": str(receipt['_id']),
            "store": parsed_data.get('merchant', f"Receipt {str(receipt['_id'])[:4]}"),
            "amount": parsed_data.get('total_amount', 0.0),
            "date": date_to_use,
            "category": parsed_data.get('category', 'Uncategorized'), # This is the overall bill category
            "items": transaction_items,
            "raw_text": receipt['extracted_text']
        })
    return jsonify(transactions), 200

@main.route('/charts/bar', methods=['GET'])
@cross_origin(supports_credentials=True, origins=["http://localhost:3000"])
@jwt_required()
def get_bar_chart_data():
    current_user_id = get_jwt_identity()
    user_receipts = get_user_receipts(current_user_id)

    daily_spending = {}
    today = datetime.utcnow().date()
    for i in range(7):
        date_key = (today - timedelta(days=i)).isoformat()
        daily_spending[date_key] = 0.0

    for receipt in user_receipts:
        if receipt.get('parsed_data') and 'date' in receipt['parsed_data'] and 'total_amount' in receipt['parsed_data']:
            receipt_date_str = receipt['parsed_data']['date']
            try:
                if isinstance(receipt_date_str, datetime):
                    receipt_date_str = receipt_date_str.isoformat().split('T')[0]

                receipt_date = datetime.fromisoformat(receipt_date_str).date()
                if receipt_date.isoformat() in daily_spending:
                    daily_spending[receipt_date.isoformat()] += receipt['parsed_data']['total_amount']
            except ValueError:
                pass

    labels = sorted(daily_spending.keys())
    data_points = [daily_spending[label] for label in labels]

    data = {
        'labels': labels,
        'datasets': [{
            'label': 'Spending per Day (Last 7 Days)',
            'backgroundColor': 'rgba(211, 47, 47, 0.7)',
            'borderColor': 'rgba(211, 47, 47, 1)',
            'borderWidth': 1,
            'hoverBackgroundColor': 'rgba(255, 102, 89, 0.8)',
            'hoverBorderColor': 'rgba(255, 102, 89, 1)',
            'data': data_points
        }]
    }
    return jsonify(data), 200

@main.route('/charts/pie', methods=['GET'])
@cross_origin(supports_credentials=True, origins=["http://localhost:3000"])
@jwt_required()
def get_pie_chart_data():
    current_user_id = get_jwt_identity()
    user_receipts = get_user_receipts(current_user_id)

    category_spending = {}
    for receipt in user_receipts:
        if receipt.get('parsed_data') and 'items' in receipt['parsed_data'] and receipt['parsed_data']['items']:
            for item in receipt['parsed_data']['items']:
                category = item.get('category', 'Uncategorized')
                amount = item.get('price', 0.0)
                if amount > 0 and category != "Non-Spend Item": # Exclude non-spend items from pie chart
                    category_spending[category] = category_spending.get(category, 0.0) + amount
        # Fallback if no items, use overall bill category and total
        elif receipt.get('parsed_data') and 'category' in receipt['parsed_data'] and 'total_amount' in receipt['parsed_data']:
            category = receipt['parsed_data']['category']
            amount = receipt['parsed_data']['total_amount']
            if amount > 0 and category != "Non-Spend Item": # Exclude non-spend items from pie chart
                category_spending[category] = category_spending.get(category, 0.0) + amount


    labels = list(category_spending.keys())
    data_points = list(category_spending.values())

    colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#E7E9ED', '#8D6E63', '#A1887F', '#C5E1A5', '#BA68C8']
    background_colors = [colors[i % len(colors)] for i in range(len(labels))]

    data = {
        'labels': labels,
        'datasets': [{
            'data': data_points,
            'backgroundColor': background_colors,
            'hoverOffset': 4
        }]
    }
    return jsonify(data), 200

@main.route('/summary', methods=['GET'])
@cross_origin(supports_credentials=True, origins=["http://localhost:3000"])
@jwt_required()
def get_spending_summary():
    current_user_id = get_jwt_identity()
    user_receipts = get_user_receipts(current_user_id)

    current_month_spending = 0.0
    last_month_spending = 0.0
    daily_spending_count = {}
    daily_spending_sum = {}

    now = datetime.utcnow()
    current_month = now.month
    current_year = now.year

    for receipt in user_receipts:
        if receipt.get('parsed_data') and 'total_amount' in receipt['parsed_data']:
            amount = receipt['parsed_data']['total_amount']
            receipt_date_str = receipt['parsed_data'].get('date')

            if receipt_date_str:
                try:
                    if isinstance(receipt_date_str, datetime):
                        receipt_date_str = receipt_date_str.isoformat().split('T')[0]

                    receipt_date = datetime.fromisoformat(receipt_date_str).date()
                    if receipt_date.month == current_month and receipt_date.year == current_year:
                        current_month_spending += amount
                        date_key = receipt_date.isoformat()
                        daily_spending_sum[date_key] = daily_spending_sum.get(date_key, 0) + amount
                        daily_spending_count[date_key] = daily_spending_count.get(date_key, 0) + 1
                    # Handle last month (e.g., if current month is Jan, last month is Dec of previous year)
                    elif receipt_date.month == ((current_month - 1) if current_month > 1 else 12) and \
                         receipt_date.year == (current_year if current_month > 1 else current_year - 1):
                        last_month_spending += amount
                except ValueError:
                    pass

    total_days_with_spending = len(daily_spending_sum)
    average_daily = (sum(daily_spending_sum.values()) / total_days_with_spending) if total_days_with_spending > 0 else 0.0

    summary = {
        "currentMonthSpending": current_month_spending,
        "lastMonthSpending": last_month_spending,
        "averageDaily": average_daily,
        "savingsRate": "N/A" # This needs actual income data to calculate
    }
    return jsonify(summary), 200

main_bp=main