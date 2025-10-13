## Cyberimmune Data Center Environmental Monitoring System

---

## Table of Contents
- [1. Problem Statement](#1-problem-statement)
- [2. Values, Damages, and Unacceptable Events](#2-values-damages-and-unacceptable-events)
- [3. Known Constraints and Initial Conditions](#3-known-constraints-and-initial-conditions)
- [4. Security Goals and Assumptions (SGA)](#4-security-goals-and-assumptions-sga)
- [5. System Architecture](#5-system-architecture)
- [6. Basic System Operation Scenario](#6-basic-system-operation-scenario)
- [7. Data Center Module Architecture](#7-data-center-module-architecture)
- [8. Negative Scenarios (Failure or Attack Cases)](#8-negative-scenarios-failure-or-attack-cases)
- [9. Architectural Decomposition](#9-architectural-decomposition)
- [10. Base Scenario for Decomposed Architecture](#10-base-scenario-for-decomposed-architecture)
- [11. Architecture Policy](#11-architecture-policy)
- [12. Quality Evaluation by Domain](#12-quality-evaluation-by-domain)
- [13. Trust Level Justification](#13-trust-level-justification)
- [14. Negative Scenario Validation](#14-negative-scenario-validation)

---

## 1. Problem Statement

The company is developing a **cyberimmune data center monitoring system** designed to ensure safe and stable operation of servers by automatically controlling the **environmental parameters** (temperature, humidity, airflow, smoke, water leakage, and power status).

The system must detect abnormal environmental conditions that may threaten equipment integrity or cause downtime. It should also guarantee **data integrity**, ensure **continuous availability**, and prevent potential **cyberattacks** aimed at disrupting operations or falsifying measurements.

---

## 2. Values, Damages, and Unacceptable Events

| Value | Negative Event | Impact Level | Comment |
|--------|----------------|---------------|-----------|
| Personnel | Overheating or smoke leads to fire hazard | High | May cause injuries, legal liability |
| Equipment | Temperature or humidity anomaly damages servers | High | Loss of assets and downtime |
| Data Integrity | Loss or alteration of monitoring data | Medium | Leads to poor maintenance decisions |
| Infrastructure | Flood or power anomaly causes system outage | High | Risk of destruction or financial losses |
| Confidential Information | Unauthorized access to system or logs | High | Cybersecurity breach and trust loss |

---

## 3. Known Constraints and Initial Conditions

- The system is implemented as a **microservice architecture** based on **Flask (Python)**.
- Communication with users occurs through a **REST API**, documented using **Swagger UI**.
- Data persistence is handled by an **SQLite** database.
- The system uses **threshold-based anomaly detection** and can be extended with **machine learning** (Isolation Forest).
- Deployment is done using **Docker** for portability.

---

## 4. Security Goals and Assumptions (SGA)

### Security Goals
- Only authenticated requests are processed.
- Environmental anomalies are detected and logged automatically.
- The system maintains integrity and availability even in case of partial failure.
- Sensitive data (sensor readings, hashes) remain unaltered and traceable.

### Security Assumptions
- Only authorized administrators access the monitoring API.
- The physical sensors are considered trusted and correctly calibrated.
- The SQLite database is stored in a protected environment.
- The Docker environment is secured from external tampering.
- Network communications occur in a controlled LAN or VPN.

---

## 5. System Architecture

**Actors:**
- **System Administrator** – interacts via Swagger UI to monitor and control the data center environment.
- **Monitoring Controller (Flask API)** – central unit processing all data and coordinating modules.
- **Physical Sensors** – measure temperature, humidity, airflow, and smoke.
- **Power & Safety Module** – monitors power and emergency signals.
- **Alert Manager** – sends alerts in case of anomaly detection.
- **SQLite Database** – stores validated sensor readings and logs.

### General Diagram System
![General diagram system](../docs/images/general_diagram.png)

### Sequence Diagram System
![Sequence diagram system](../docs/images/sequence_diagram.png)

### Data Center Architecture
![Data center architecture](../docs/images/datacenter_architecture.png)

### Basic scenario for data center operation
![Basic scenario for data center operation](../docs/images/datacenter_operation.png)

---

## 6. Basic System Operation Scenario

1. The administrator accesses **Swagger UI**.
2. They call the endpoint **`/datacenter/monitor`** with environmental data.
3. The **Flask API** validates the input and checks for anomalies.
4. If conditions are normal, the data is **stored in the SQLite database**.
5. If an anomaly is detected, the API returns a **400 error** and **does not store** the data.
6. The administrator can query **`/datacenter/history`** or **`/datacenter/status`** for reports.

---

## 7. Data Center Module Architecture

| **Component** | **Description** |
|----------------|-----------------|
| **Monitoring Controller (Flask API)** | Central logic handling data requests, anomaly detection, and alert triggering. |
| **Sensor Interface** | Connects to environmental sensors (temperature, humidity, airflow, smoke). |
| **Power & Safety Module** | Monitors electrical status and detects emergency conditions (fire, outage). |
| **Database Layer (SQLite)** | Stores validated measurements and historical logs. |
| **Integrity Module** | Validates the consistency of stored data using SHA-256 hashing. |
| **Alert Manager** | Sends alerts to the administrator when anomalies are detected. |
| **Swagger UI** | User interface for monitoring and API interaction. |

---

## 8. Negative Scenarios (Failure or Attack Cases)

Below are identified negative scenarios that may affect the cyberimmune data center system. Each scenario is linked to a risk mitigation strategy.

| ID   | Description                                | Impact | Mitigation                                   |
| ---- | ------------------------------------------ | ------ | -------------------------------------------- |
| NS-1 | Temperature sensor sends false high values | Medium | Validate readings and compare averages       |
| NS-2 | Database corruption or hash mismatch       | High   | Integrity verification before each query     |
| NS-3 | Unauthorized API access                    | High   | Require authentication and IP restriction    |
| NS-4 | Data loss during Docker restart            | Medium | Persist volumes and create backups           |
| NS-5 | Power outage interrupts measurement        | Medium | Reboot recovery and status resynchronization |
| NS-6 | Flood detection false positive             | Low    | Cross-check with humidity and airflow        |

## 10. Sequence Diagrams for Negative Scenarios

---

### NS-1 – False High Temperature Reading
```plantuml
@startuml
title NS-1 – False High Temperature Reading

actor Admin
participant "Flask API / Monitoring Controller" as API
participant "Temp Control" as Temp
participant "Alert & Logs" as Alert
database "SQLite Database" as DB

Admin -> API : Send environmental data (temperature)
API -> Temp : Validate temperature
Temp --> API : Return abnormally high value
API -> API : Detect anomaly (threshold exceeded)
API -> Alert : Log anomaly and notify admin
Alert --> API : Log confirmed
API --> Admin : HTTP 400 {"error": "Temperature anomaly detected"}
@enduml

---

## 9. Architectural Decomposition

The architecture is decomposed into modular components, each responsible for a specific functionality. This separation allows for fault isolation, simplified maintenance, and better security management.

| Module                                | Description                   | Responsibilities                                                       | Interaction                               |
| ------------------------------------- | ----------------------------- | ---------------------------------------------------------------------- | ----------------------------------------- |
| **Flask API / Monitoring Controller** | Central coordination layer    | • Handles requests, orchestrates modules, manages detection and alerts | Communicates with sensors, DB, and alerts |
| **Temp Control**                      | Temperature management module | • Reads temperature, checks thresholds                                 | Responds to Flask API                     |
| **Humidity & Air**                    | Controls humidity and airflow | • Ensures proper environmental flow and humidity                       | Works under Flask API                     |
| **Power Monitor**                     | Power stability tracking      | • Detects power faults or instability                                  | Sends results to Flask API                |
| **SQLite Database**                   | Local data store              | • Saves valid readings only, ensures data integrity                    | Receives only validated data              |
| **Alert & Logs**                      | Logging and alerts module     | • Logs anomalies and sends notifications                               | Triggered by Flask API                    |


---

## 10. Base Scenario for Decomposed Architecture

1. Administrator triggers monitoring via Swagger UI.
2. Flask API (Monitoring Controller) requests readings from sensors and power module.
3. Data is sent to the Integrity Checker for validation.
4. If integrity passes and values are within limits, data is stored in the database.
5. If an anomaly is detected (e.g., overheating, power fault), the Alert Manager sends a notification and data is not stored.
6. Administrator can view logs and alerts from Swagger UI.


---

## 11. Architecture Policy

- Data must be verified before insertion.
- System must handle abnormal inputs gracefully.
- Only trusted Docker images are deployed.
- Logs and history are retained for auditing.
- No data is stored if anomaly is detected.

---

## 12. Quality Evaluation by Domain

| Domain | Quality Attribute | Level |
|---------|-------------------|--------|
| Reliability | Continuous monitoring and fault tolerance | High |
| Integrity | SHA-256 checksum verification | High |
| Availability | Dockerized and restartable service | High |
| Maintainability | Modular Python code (Flask + SQLite) | High |
| Usability | Swagger UI interface | Medium |

---

## 13. Trust Level Justification

- **SQLite Database** – trusted local storage, minimal attack surface.
- **Flask API** – verified Python runtime, open-source dependencies.
- **Docker Container** – ensures isolation and reproducibility.
- **Sensors** – assumed trusted, may require calibration.

---

## 14. Negative Scenario Validation

### NSV-1: Temperature Anomaly Simulation
- Input: `{"temperature": 60}`
- Output: HTTP 400 – `{"error": "Environmental anomaly detected!"}`
- Validation: System reacts correctly.

### NSV-2: Normal Environment
- Input: `{"temperature": 45, "humidity": 50, "airflow": 3}`
- Output: HTTP 200 – normal state stored in database.
- Validation: Data is recorded only if valid.

---

**Conclusion:**  
The Data Center Monitoring System successfully implements environmental anomaly detection, data integrity verification, and secure data recording using a Flask-based architecture. The system is modular, secure, and extensible for future cyberimmunity features.

