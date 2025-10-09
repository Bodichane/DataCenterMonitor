from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_cors import CORS
import random
import hashlib
import json
import sqlite3
import time
import logging
import os
from datetime import datetime
from sklearn.ensemble import IsolationForest
import numpy as np

# ============================
# GLOBAL CONFIGURATION
# ============================

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for Swagger UI

# Swagger configuration
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "DataCenter Monitor API",
        "description": "Datacenter monitoring API with anomaly detection and history tracking",
        "version": "1.0.0"
    },
    "host": "127.0.0.1:8080",  # ✅ Use local address for Swagger
    "basePath": "/",
    "schemes": ["http", "https"],  # ✅ Compatible with HTTP and HTTPS
}
swagger = Swagger(app, template=swagger_template)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "datacenter.db")
JSON_PATH = os.path.join(DATA_DIR, "data.json")

# ============================
# UTILITY FUNCTIONS
# ============================

def simulate_temperature():
    temp = random.uniform(20, 40)
    if random.random() < 0.1:
        temp = random.uniform(50, 70)
    return temp


def save_data(data, filename=JSON_PATH):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        json.dump(data, f)
    with open(filename, "rb") as f:
        hash_value = hashlib.sha256(f.read()).hexdigest()
    return hash_value


def check_integrity(expected_hash, filename=JSON_PATH):
    with open(filename, "rb") as f:
        current_hash = hashlib.sha256(f.read()).hexdigest()
    return current_hash == expected_hash


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS temperatures
                 (id TEXT, server_id INTEGER, temperature REAL, timestamp REAL)''')
    conn.commit()
    conn.close()


def seed_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM temperatures")
    count = c.fetchone()[0]
    if count < 10:
        for i in range(10 - count):
            temp = random.uniform(20, 40)
            timestamp = time.time() - i * 60
            id = hashlib.md5(str(timestamp).encode()).hexdigest()
            c.execute("INSERT INTO temperatures (id, server_id, temperature, timestamp) VALUES (?, ?, ?, ?)",
                      (id, 1, temp, timestamp))
        conn.commit()
    conn.close()


def detect_anomaly(temperatures):
    model = IsolationForest(contamination=0.1, random_state=42)
    temps = np.array(temperatures).reshape(-1, 1)
    predictions = model.fit_predict(temps)
    return predictions[-1] == -1


# ============================
# INITIALIZATION
# ============================

init_db()
seed_db()

# ============================
# FLASK ROUTES WITH SWAGGER
# ============================

@app.route("/datacenter/monitor", methods=["POST"])
def monitor():
    """
    Records a temperature for a given server
    ---
    tags:
      - Monitoring
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            server_id:
              type: integer
              example: 1
            temperature:
              type: number
              example: 45
    responses:
      200:
        description: Data recorded successfully
      400:
        description: Anomalous temperature detected
    """
    data = request.get_json(force=True)
    server_id = data.get("server_id", 1)
    temp = data.get("temperature", simulate_temperature())

    timestamp = time.time()
    id = hashlib.md5(str(timestamp).encode()).hexdigest()

    if temp > 50:
        return jsonify({"error": "Anomalous temperature detected!"}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT temperature FROM temperatures ORDER BY timestamp DESC LIMIT 10")
    recent_temps = [row[0] for row in c.fetchall()]
    recent_temps.append(temp)

    if detect_anomaly(recent_temps):
        conn.close()
        return jsonify({"error": "Anomalous temperature detected!"}), 400

    c.execute("INSERT INTO temperatures (id, server_id, temperature, timestamp) VALUES (?, ?, ?, ?)",
              (id, server_id, temp, timestamp))
    conn.commit()
    conn.close()

    result = {"id": id, "server_id": server_id, "temperature": temp, "timestamp": timestamp}
    hash_value = save_data(result)
    if not check_integrity(hash_value):
        return jsonify({"error": "Data corruption detected!"}), 400

    return jsonify(result), 200


@app.route("/datacenter/history", methods=["GET"])
def history():
    """
    Returns the last 10 recorded measurements
    ---
    tags:
      - Monitoring
    responses:
      200:
        description: List of recent measurements
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, server_id, temperature, timestamp FROM temperatures ORDER BY timestamp DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()

    data = [
        {
            "id": row[0],
            "server_id": row[1],
            "temperature": row[2],
            "timestamp": row[3],
            "date": datetime.fromtimestamp(row[3]).strftime("%Y-%m-%d %H:%M:%S")
        }
        for row in rows
    ]
    return jsonify(data), 200


@app.route("/datacenter/status", methods=["GET"])
def status():
    """
    Returns the general status of the system
    ---
    tags:
      - System
    responses:
      200:
        description: Current datacenter status
    """
    return jsonify({"status": "System operational", "last_backup": time.time()}), 200


# ============================
# SERVER LAUNCH
# ============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
