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

# ============================
# GLOBAL CONFIGURATION
# ============================

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for Swagger UI

# Swagger configuration
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "DataCenter Monitor API",
        "description": "DataCenter monitoring API with environmental anomaly detection and history",
        "version": "1.0.0"
    },
    "host": "127.0.0.1:8080",
    "basePath": "/",
    "schemes": ["http", "https"],
}
swagger = Swagger(app, template=swagger_template)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "datacenter.db")
JSON_PATH = os.path.join(DATA_DIR, "data.json")

# ============================
# UTILITY FUNCTIONS
# ============================

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
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS environment
                     (id TEXT, server_id INTEGER, temperature REAL, humidity REAL,
                      airflow REAL, smoke_detected BOOLEAN, water_leak BOOLEAN,
                      power_status TEXT, timestamp REAL)''')
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        conn.close()

def seed_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM environment")
        count = c.fetchone()[0]
        if count < 10:
            for i in range(10 - count):
                timestamp = time.time() - i * 60
                id = hashlib.sha256(str(timestamp).encode()).hexdigest()
                c.execute("INSERT INTO environment (id, server_id, temperature, humidity, airflow, smoke_detected, water_leak, power_status, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (id, 1, random.uniform(20, 40), random.uniform(30, 60), random.uniform(1, 5), False, False, "OK", timestamp))
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database seeding error: {e}")
        raise
    finally:
        conn.close()

def detect_anomaly(env):
    """Simple rule-based anomaly detection"""
    if env["temperature"] > 50:
        return True
    if env["humidity"] > 80:
        return True
    if env["airflow"] < 1:
        return True
    if env["smoke_detected"]:
        return True
    if env["water_leak"]:
        return True
    if env["power_status"] != "OK":
        return True
    return False

# ============================
# INITIALIZATION
# ============================

init_db()
seed_db()

# ============================
# FLASK ROUTES
# ============================

@app.route("/datacenter/monitor", methods=["POST"])
def monitor():
    """
    Record environmental data for a given server
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
            humidity:
              type: number
              example: 50
            airflow:
              type: number
              example: 3
            smoke_detected:
              type: boolean
              example: false
            water_leak:
              type: boolean
              example: false
            power_status:
              type: string
              example: "OK"
    responses:
      200:
        description: Data successfully recorded
      400:
        description: Environmental anomaly detected
      500:
        description: Database error
    """
    data = request.get_json(force=True)
    required_keys = ["server_id", "temperature", "humidity", "airflow", "smoke_detected", "water_leak", "power_status"]

    # Check for missing fields
    for key in required_keys:
        if key not in data:
            return jsonify({"error": f"Missing field: {key}"}), 400

    env = {
        "server_id": data["server_id"],
        "temperature": data["temperature"],
        "humidity": data["humidity"],
        "airflow": data["airflow"],
        "smoke_detected": data["smoke_detected"],
        "water_leak": data["water_leak"],
        "power_status": data["power_status"]
    }

    logger.info(f"Received environment data: {env}")

    # Detect anomalies
    if detect_anomaly(env):
        logger.warning(f"⚠️ Anomaly detected for server {env['server_id']}: {env}")
        return jsonify({"error": "Environmental anomaly detected!"}), 400

    timestamp = time.time()
    env_id = hashlib.sha256(str(timestamp).encode()).hexdigest()

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO environment (id, server_id, temperature, humidity, airflow, smoke_detected, water_leak, power_status, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (env_id, env["server_id"], env["temperature"], env["humidity"], env["airflow"], env["smoke_detected"], env["water_leak"], env["power_status"], timestamp))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database insertion error: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        conn.close()

    result = env.copy()
    result.update({"id": env_id, "timestamp": timestamp})
    hash_value = save_data(result)
    if not check_integrity(hash_value):
        return jsonify({"error": "Data corruption detected!"}), 400

    return jsonify(result), 200

@app.route("/datacenter/history", methods=["GET"])
def history():
    """
    Return the 10 most recent environmental measurements
    ---
    tags:
      - Monitoring
    responses:
      200:
        description: Recent measurements list
      500:
        description: Database error
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, server_id, temperature, humidity, airflow, smoke_detected, water_leak, power_status, timestamp FROM environment ORDER BY timestamp DESC LIMIT 10")
        rows = c.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Database query error: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        conn.close()

    data = [
        {
            "id": row[0],
            "server_id": row[1],
            "temperature": row[2],
            "humidity": row[3],
            "airflow": row[4],
            "smoke_detected": bool(row[5]),
            "water_leak": bool(row[6]),
            "power_status": row[7],
            "timestamp": row[8],
            "date": datetime.fromtimestamp(row[8]).strftime("%Y-%m-%d %H:%M:%S")
        }
        for row in rows
    ]
    return jsonify(data), 200

@app.route("/datacenter/status", methods=["GET"])
def status():
    """
    Return overall system status
    ---
    tags:
      - System
    responses:
      200:
        description: Current status of the datacenter
    """
    return jsonify({"status": "Operational", "last_updated": time.time()}), 200

# ============================
# SERVER LAUNCH
# ============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)