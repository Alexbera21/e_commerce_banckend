from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "ecommerce_db")

print(f"✅ Conectando a base de datos: {DATABASE_NAME}")

client = AsyncIOMotorClient(MONGO_URL)
database = client[DATABASE_NAME]

user_collection    = database.get_collection("users")
product_collection = database.get_collection("products")
order_collection   = database.get_collection("orders")
cart_collection    = database.get_collection("carts")
review_collection = database.get_collection("reviews")