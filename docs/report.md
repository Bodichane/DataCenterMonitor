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
- **System Administrator:** Interacts with the Swagger UI to view status and trigger monitoring.
- **Flask API Server:** Central controller handling requests and data processing.
- **Physical Sensors:** Provide real-time environmental measurements.
- **SQLite Database:** Stores validated and verified measurements.

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

### Components

### 🧩 Data Center Module Architecture

The data center architecture consists of interconnected modules managed by the central **Flask API / Monitoring Controller**, ensuring reliability, data integrity, and automated anomaly detection across all subsystems.

| **Component** | **Description** |
|----------------|----------------|
| **Flask API / Monitoring Controller** | Central processing unit managing API calls, anomaly detection, and coordination between all subsystems. |
| **Temperature Control Module** | Monitors and regulates temperature levels using environmental sensors. |
| **Humidity & Air Module** | Tracks humidity and airflow consistency to maintain optimal greenhouse conditions. |
| **Power Monitor** | Detects power fluctuations and ensures electrical stability across modules. |
| **SQLite Database** | Stores validated sensor data, configuration parameters, and anomaly logs. |
| **Alert & Logs** | Handles alert notifications, error tracking, and system event logging. |
| **Docker Network** | Provides a secure, isolated, and portable deployment environment for the entire system. |


---

## 8. Negative Scenarios (Failure or Attack Cases)

| ID | Description | Impact | Mitigation |
|----|--------------|---------|-------------|
| NS-1 | Temperature sensor sends false high values | Medium | Validate readings and compare averages |
| NS-2 | Database corruption or hash mismatch | High | Integrity verification before each query |
| NS-3 | Unauthorized API access | High | Require authentication and IP restriction |
| NS-4 | Data loss during Docker restart | Medium | Persist volumes and create backups |
| NS-5 | Power outage interrupts measurement | Medium | Reboot recovery and status resynchronization |
| NS-6 | Flood detection false positive | Low | Cross-check with humidity and airflow |

---

## 9. Architectural Decomposition

| Module | Responsibilities |
|---------|------------------|
| **Monitoring API** | Receives sensor data, analyzes anomalies |
| **Database Manager** | Stores and retrieves data |
| **Integrity Checker** | Verifies SHA-256 hash of data.json |
| **Swagger Interface** | Provides REST interface for users |
| **Docker Environment** | Isolates the runtime and dependencies |

---

## 10. Base Scenario for Decomposed Architecture

1. Administrator sends environmental data through Swagger UI.
2. Flask API validates and forwards it to the integrity checker.
3. If integrity passes, data is stored in the database.
4. In case of anomaly, the API blocks storage and returns an alert.
5. Admin can consult system logs or history.

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

