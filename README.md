# 🧠 DataCenter Monitor

**DataCenter Monitor** is a Flask API that monitors the temperature of servers in a data center.  
It detects thermal anomalies using an **Isolation Forest** model, stores data in an **SQLite** database, and provides interactive documentation via **Swagger UI**.

---

## 🚀 Features

- **Complete REST API** with Flask  
- **Anomaly detection** via `scikit-learn`  
- Integrated **SQLite database**  
- **Data integrity** verified by SHA-256 fingerprint  
- **Swagger UI** for easy endpoint testing  
- **Simplified deployment with Docker**

---

## 🐳 Deployment with Docker
### Installation

#### 1️⃣ Clone the repository
```bash
git clone https://github.com/Bodichane/DataCenterMonitor.git
cd DataCenterMonitor
```
#### 2️⃣ Build the Docker image
```bash
docker build -t datacentermonitor .
docker run -p 8080:8080 datacentermonitor
```

## 🌐 Usage

In the browser address bar, enter http://localhost:8080/apidocs.

Using the Swagger UI graphical interface, start the monitoring process by selecting the REST API /datacenter/monitor method and entering the following test parameters:

Test parameters:
```
{
  “server_id”: 1,
  “temperature”: 45
}
```

To test anomaly detection, use :
```
{
  “server_id”: 1,
  “temperature”: 60
}
```

The response to this last request should be:

`{“error”: “Abnormal temperature detected!”}`


You can then view the measurement history with /datacenter/history and check the overall status of the system with /datacenter/status, without needing to provide any additional parameters
