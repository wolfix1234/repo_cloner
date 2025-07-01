from flask import Flask, request, jsonify
import subprocess
import threading
import os
import requests
from dotenv import load_dotenv
import base64

load_dotenv()

app = Flask(__name__)

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
PORT_BASE = 3000
next_port = PORT_BASE
port_lock = threading.Lock()

def build_image(force_rebuild=False):
    print("Building Docker image...")
    cmd = ["docker", "build", "-t", "child_image", "."]
    if force_rebuild:
        cmd.insert(3, "--no-cache")
    subprocess.run(cmd, check=True)

def extract_repo_name(repo_url):
    return os.path.splitext(repo_url.rstrip('/').split('/')[-1])[0]

def run_container(repo_url, port):
    repo_name = extract_repo_name(repo_url)
    container_name = f"child_{port}_{repo_name}"

    print(f"Deploying on port: {port}")
    print(f"Starting container {container_name} for repo: {repo_url} on port {port}")

    subprocess.run([
        "docker", "run", "-d",
        "--name", container_name,
        "--cpus", "1.0",
        "-e", f"REPO_URL={repo_url}",
        "-e", f"PORT={port}",
        "-p", f"{port}:{port}",
        "child_image"
    ], check=True)

@app.route('/deploy', methods=['POST'])
def deploy():
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Extract and decode the Base64 token
        encoded_token = auth_header.split("Bearer ")[1].strip()
        decoded_token = base64.b64decode(encoded_token).decode("utf-8")
    except Exception:
        return jsonify({"error": "Invalid token format"}), 401

    if decoded_token != AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    global next_port
    data = request.json
    repo_url = data.get("repo_url")
    if not repo_url:
        return jsonify({"error": "Missing repo_url"}), 400

    try:
        response = requests.get(repo_url, timeout=10)
        if response.status_code != 200:
            return jsonify({"error": f"Repo URL returned status code {response.status_code}"}), 400
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to reach repo URL: {e}"}), 400

    with port_lock:
        port = next_port
        next_port += 1

    try:
        build_image()
        run_container(repo_url, port)
        return jsonify({"status": "success", "port": port}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
