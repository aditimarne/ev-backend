---
title: EV Battery Health Prediction API
emoji: ⚡
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
---

# ⚡ EV Battery Health Prediction API

A **FastAPI-based ML backend** that predicts:

- **SOH (State of Health)**
- **RUL (Remaining Useful Life)**

for **OLA** and **Revolt** electric vehicles.

Built with:
- FastAPI
- TensorFlow (LSTM)
- XGBoost
- MongoDB Atlas (GridFS)
- Scikit-learn

---

## 🚀 Features

- OLA battery predictions
- Revolt battery predictions
- Intelligent battery usage recommendations
- ML models loaded lazily (cold-start safe)
- 100% free deployment on Hugging Face Spaces

---

## 🔌 API Endpoints

### OLA
- `POST /ola/predict`
- `POST /ola/recommendations`

### Revolt
- `POST /revolt/predict`
- `POST /revolt/recommendations`

Swagger UI:
