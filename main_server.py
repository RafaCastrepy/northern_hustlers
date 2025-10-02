import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Ensure the file exists
DATA_FILE = "contact_data.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        f.write("[]")  # Start with an empty JSON array

@app.route("/")
def home():
    return "Welcome to the Flask Server!"

@app.route('/run')
def run_bat():
    try:
        os.system(r'start startit.bat')  # Use 'start' to open a separate process
        return jsonify({"message": "its time to hustle..."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/save", methods=["POST"])
def save_form():
    try:
        data = request.json  # Get JSON data from the request

        # Load existing data
        with open(DATA_FILE, "r") as file:
            existing_data = json.load(file)
            print("opened")

        # Append new data
        existing_data.append(data)
        print("appended")
        # Save updated data
        with open(DATA_FILE, "w") as file:
            json.dump(existing_data, file, indent=4)

        return jsonify({"message": "Data saved successfully!"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)  # Single server running on port 5000
