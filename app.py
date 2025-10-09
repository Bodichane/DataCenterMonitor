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
# CONFIGURATION GLOBALE
# ============================

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # ✅ Active CORS pour Swagger UI

# Configuration Swagger
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "DataCenter Monitor API",
        "description": "API de surveillance du datacenter avec détection d’anomalies et historique",
        "version": "1.0.0"
    },
    "host": "127.0.0.1:8080",  # ✅ Utiliser l’adresse locale pour Swagger
    "basePath": "/",
    "schemes": ["http", "https"],  # ✅ Compatible avec HTTP et HTTPS
}
swagger = Swagger(app, template=swagger_template)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "datacenter.db")
JSON_PATH = os.path.join(DATA_DIR, "data.json")

# ============================
# FONCTIONS UTILITAIRES
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
# INITIALISATION
# ============================

init_db()
seed_db()

# ============================
# ROUTES FLASK AVEC SWAGGER
# ============================

@app.route("/datacenter/monitor", methods=["POST"])
def monitor():
    """
    Enregistre une température pour un serveur donné
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
        description: Données enregistrées avec succès
      400:
        description: Température anormale détectée
    """
    data = request.get_json(force=True)
    server_id = data.get("server_id", 1)
    temp = data.get("temperature", simulate_temperature())

    timestamp = time.time()
    id = hashlib.md5(str(timestamp).encode()).hexdigest()

    if temp > 50:
        return jsonify({"error": "Température anormale détectée!"}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT temperature FROM temperatures ORDER BY timestamp DESC LIMIT 10")
    recent_temps = [row[0] for row in c.fetchall()]
    recent_temps.append(temp)

    if detect_anomaly(recent_temps):
        conn.close()
        return jsonify({"error": "Température anormale détectée!"}), 400

    c.execute("INSERT INTO temperatures (id, server_id, temperature, timestamp) VALUES (?, ?, ?, ?)",
              (id, server_id, temp, timestamp))
    conn.commit()
    conn.close()

    result = {"id": id, "server_id": server_id, "temperature": temp, "timestamp": timestamp}
    hash_value = save_data(result)
    if not check_integrity(hash_value):
        return jsonify({"error": "Corruption des données détectée!"}), 400

    return jsonify(result), 200


@app.route("/datacenter/history", methods=["GET"])
def history():
    """
    Retourne les 10 dernières mesures enregistrées
    ---
    tags:
      - Monitoring
    responses:
      200:
        description: Liste des mesures récentes
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
    Donne l’état général du système
    ---
    tags:
      - Système
    responses:
      200:
        description: Statut actuel du datacenter
    """
    return jsonify({"status": "Système opérationnel", "last_backup": time.time()}), 200


# ============================
# LANCEMENT SERVEUR
# ============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
