from flask import Flask, request, jsonify
import os
import json
import re
import sys
from dotenv import load_dotenv
import base64

load_dotenv()

app = Flask(__name__)
AUTH_TOKEN = os.getenv("AUTH_TOKEN")


@app.route('/update_json', methods=['POST'])
def update_json():
    auth_header = request.headers.get("Authorization")
    
    #print(f"Decoded: {decoded_token} | Expected: {AUTH_TOKEN}")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized not parse correctly"}), 401

    try:
        # Extract and decode the Base64 token
        encoded_token = auth_header.split("Bearer ")[1].strip()
        decoded_token = base64.b64decode(encoded_token).decode("utf-8")
    except Exception:
        return jsonify({"error": "Invalid token format"}), 401

    if decoded_token != AUTH_TOKEN:
        return jsonify({"error": "Unauthorized envalid"}), 401

    data = request.json
    repo_name = data.get('repo_name')
    file_name = data.get('file_name')
    json_content = data.get('json_content')
    print(data, "json data")

    if not repo_name or not file_name or not json_content:
        return jsonify({"error": "Missing repo_name, file_name, or json_content"}), 400

    # Validate file_name (basic security)
    if not re.match(r'^[\w-]+$', file_name):
        return jsonify({"error": "Invalid file_name"}), 400

    # Write to /app_data/{repo_name}/public/{file_name}.json
    file_path = f'/app/{repo_name}/public/{file_name}.json'

    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(json_content)  # json_content is expected as a raw JSON string
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    repo_name = sys.argv[1]
    print("JSON_UPDATE_PORT:", os.getenv("JSON_UPDATE_PORT"))
    port = int(os.getenv("JSON_UPDATE_PORT", 4000))
    app.run(host="0.0.0.0", port=port)


