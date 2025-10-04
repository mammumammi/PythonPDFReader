# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import find

app = Flask(__name__)
CORS(app)  # Allow React frontend to call this backend

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Save PDF temporarily
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    print("Received file:", file.filename)

    # Extract data
    try:
        extracted_data = find.read_pdf(file_path)
        print("Extracted data:", extracted_data)
    except Exception as e:
        print("Error reading PDF:", e)
        return jsonify({"error": str(e)}), 500

    # Push to Google Sheets
    try:
        find.push_to_sheet(extracted_data)
    except Exception as e:
        print("Error pushing to Google Sheets:", e)
        return jsonify({"error": str(e)}), 500

    return jsonify(extracted_data)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
