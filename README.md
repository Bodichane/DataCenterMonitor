# 🧠 DataCenter Monitor

**DataCenter Monitor** est une API Flask permettant de surveiller la température des serveurs dans un datacenter.  
Elle détecte les anomalies thermiques grâce à un modèle **Isolation Forest**, stocke les données dans une base **SQLite** et fournit une documentation interactive via **Swagger UI**.

---

## 🚀 Fonctionnalités

- **API REST complète** avec Flask  
- **Détection d’anomalies** via `scikit-learn`  
- **Base de données SQLite** intégrée  
- **Intégrité des données** vérifiée par empreinte SHA-256  
- **Swagger UI** pour tester facilement les endpoints  
- **Déploiement simplifié avec Docker**

---

## 🐳 Déploiement avec Docker
### Installation

#### 1️⃣ Cloner le dépôt
```bash
git clone https://github.com/Bodichane/DataCenterMonitor.git
cd DataCenterMonitor
```
#### 2️⃣ Construire l’image Docker
```bash
docker build -t datacentermonitor .
docker run -p 8080:8080 datacentermonitor
```

## 🌐 Utilisation

Dans la barre d'adresse du navigateur, saisissez http://localhost:8080/apidocs
.
À l'aide de l'interface graphique Swagger UI, lancez le processus de surveillance en sélectionnant la méthode REST API /datacenter/monitor et en saisissant les paramètres de test suivants :

Paramètres de test :
```
{
  "server_id": 1,
  "temperature": 45
}
```

Pour tester la détection d’anomalie, utilisez :
```
{
  "server_id": 1,
  "temperature": 60
}
```

Le retour de cette dernière requête devrait être :

`{"error": "Température anormale détectée!"}`


Ensuite, vous pouvez consulter l’historique des mesures avec /datacenter/history et vérifier l’état général du système avec /datacenter/status, sans avoir besoin de fournir de paramètres supplémentaires.


