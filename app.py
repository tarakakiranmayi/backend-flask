from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from datetime import datetime
from bson.objectid import ObjectId
import re

# Regular expression for email validation
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# Initialize Flask application
app = Flask(__name__)

# Configure MongoDB connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/flaskdatabase"
mongo = PyMongo(app)

# Root route to check if the server is running
@app.route("/")
def home():
    return "Hello, Flask is running!"

# API to create a new user
@app.route("/createUser", methods=["POST"])
def create_user():
    data = request.get_json()
    
    # Validate input data
    if "age" not in data or not isinstance(data["age"], (int, float)) or data["age"] < 0:
        return jsonify({"error": "Invalid age. Age must be a non-negative number."}), 400
    
    if "email" not in data or not re.match(EMAIL_REGEX, data["email"]):
        return jsonify({"error": "Invalid email format."}), 400
    
    # Check if the user already exists
    if mongo.db.User.find_one({"email": data["email"]}):
        return jsonify({"message": "User already exists!"}), 409  # 409 Conflict
    
    # Insert the new user into the database
    mongo.db.User.insert_one({
        "name": data["name"],
        "email": data["email"],
        "age": data["age"],
        "created_at": datetime.now()
    })
    
    return jsonify({"message": "User created successfully!"}), 201  # 201 Created

# API to fetch all users
@app.route("/getUsers", methods=["GET"])
def get_users():
    users = mongo.db.User.find()
    user_list = []
    
    # Convert MongoDB ObjectId to string for JSON serialization
    for user in users:
        user["_id"] = str(user["_id"])
        user_list.append(user)
    
    return jsonify(user_list)

# API to update an existing user
@app.route("/updateUser/<id>", methods=["PUT"])
def update_user(id):
    data = request.get_json()
    user = mongo.db.User.find_one({"_id": ObjectId(id)})
    
    if user:
        mongo.db.User.update_one({"_id": ObjectId(id)}, {"$set": data})
        return jsonify({"message": "User updated successfully!"})
    else:
        return jsonify({"error": "User not found!"}), 404  # 404 Not Found

# API to delete a user
@app.route("/deleteUser/<id>", methods=["DELETE"])
def delete_user(id):
    user = mongo.db.User.find_one({"_id": ObjectId(id)})
    
    if user:
        mongo.db.User.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "User deleted successfully!"})
    else:
        return jsonify({"error": "User not found!"}), 404  # 404 Not Found

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)  # Enable debug mode for development