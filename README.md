# Fraud Detection System - Take-Home Test

This project implements a complete machine learning solution for detecting fraudulent transactions, including exploratory data analysis, model training, and a production-ready REST API service.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Dependencies](#dependencies)
- [Setup Instructions](#setup-instructions)
- [Running the Complete Workflow](#running-the-complete-workflow)
- [API Testing](#api-testing)
- [Docker Deployment](#docker-deployment)
- [Architecture & Business Recommendations](#architecture--business-recommendations)

## 🎯 Project Overview

**Deliverables Completed:**
1. ✅ **Exploratory Data Analysis (EDA)** - `Training.ipynb`
2. ✅ **Model Training** - `Training.ipynb` 
3. ✅ **Model Serving API** - `app.py`
4. ✅ **System Architecture Design** - See architecture section below

**Key Features:**
- XGBoost classifier with 98% precision and 100% recall on fraud detection
- REST API with automatic fraud flagging and storage
- SQLite database for persistent storage of flagged transactions
- Dockerized deployment option
- Comprehensive data analysis and model evaluation

## 📦 Dependencies

**System Requirements:**
- **Docker:** Latest version with Docker Compose
- **Docker Compose:** v2.0 or higher
- **Available Ports:** 8888 (training), 5001 (API), 8501 (web interface)
- **Disk Space:** ~2GB for Docker images and dataset
- **Memory:** 4GB RAM recommended for training

**All Python dependencies are automatically handled by Docker containers:**
- **Core API:** Flask, scikit-learn, xgboost, pandas, joblib
- **Training:** Jupyter, numpy, matplotlib, seaborn, gdown
- **Web Interface:** Streamlit, requests

**No manual Python installation required - everything runs in Docker!**

## 🚀 Setup Instructions

**Prerequisites:** Ensure Docker and Docker Compose are installed on your system.

### Step 1: Clone Repository
```bash
git clone https://github.com/tumrabert/FraudDetecion
FraudDetecioncd FraudDetecion
```

**That's it! No additional setup required - Docker handles everything.**

## 🔄 Running the Complete Workflow

### Step 1 & 2: Run EDA and Model Training

**Single Docker Command:**
```bash
# Start Jupyter Lab environment for training
docker-compose -f docker-compose.training.yml up --build
```

**Access the training environment:**
- **URL:** http://localhost:8888
- **Token:** `fraud_detection_training`

**Training Instructions (CRITICAL - Follow Exactly):**
1. Wait for the Docker container to fully start (you'll see "Jupyter server is running")
2. Open your browser and go to http://localhost:8888
3. Enter token: `fraud_detection_training`
4. Click on `Training.ipynb` to open the notebook
5. **Execute ALL cells in sequence** - this will:
   - Download 6.36M transaction dataset from Google Drive
   - Perform comprehensive EDA revealing key fraud patterns
   - Engineer features and handle class imbalance
   - Train XGBoost model with 98% precision and 100% recall
   - Save the complete model pipeline to `model/fraud_model.joblib`
6. **IMPORTANT:** Ensure the final cell saves the model to `model/fraud_model.joblib`
7. When training is complete, stop the container: `Ctrl+C`

**Expected Output:** A trained model file at `model/fraud_model.joblib` (271KB)

### Step 3: Model Serving (API and Storage)

**Prerequisites:** Ensure Step 1-2 is completed and `model/fraud_model.joblib` exists.

**Single Docker Command:**
```bash
# Start the complete API stack with web interface
docker-compose -f docker-compose.api.yml up --build
```

**Expected Startup Output:**
```
fraud-detection-api-1  | Model loaded successfully.
fraud-detection-api-1  |  * Running on all addresses (0.0.0.0)
fraud-detection-api-1  |  * Running on http://127.0.0.1:5000
streamlit-ui-1         | You can now view your Streamlit app in your browser.
streamlit-ui-1         | URL: http://0.0.0.0:8501
```

**Access the services:**
- **Fraud Detection API:** http://localhost:5001
- **Streamlit Web Interface:** http://localhost:8501

**Services included:**
- Flask REST API with trained XGBoost model
- SQLite database for persistent fraud storage
- Streamlit web interface for interactive testing
- Automatic health checks and restart policies
- Automatic health checks and restart policies

## 🧪 Testing the System

### Method 1: Streamlit Web Interface (Recommended)

**Step-by-step testing procedure:**

1. **Verify services are running:**
   - API should be accessible at http://localhost:5001
   - Web interface should be accessible at http://localhost:8501

2. **Open the web interface:**
   - Navigate to http://localhost:8501 in your browser
   - You should see "🚨 Fraud Detection API Tester"

3. **Test API health:**
   - Click "Check API Health" button
   - Expected result: ✅ API is healthy with `{"model_loaded": true}`

4. **Test fraud prediction:**
   - Use the "Predefined Examples" tab
   - Select "Fraudulent Transfer" and click "🧪 Test Selected Example"
   - Expected result: 🚨 **FRAUD DETECTED**
   - Select "Legitimate Payment" and test
   - Expected result: ✅ **LEGITIMATE**

5. **View flagged transactions:**
   - Click "🔄 Refresh Flagged Transactions"
   - Should show previously flagged fraudulent transactions

### Method 2: Direct API Testing (Advanced)

**Health Check:**
```bash
curl http://localhost:5001/health
# Expected: {"status": "healthy", "model_loaded": true}
```

**Test Fraud Detection:**
```bash
# Test 1: Fraudulent TRANSFER (empties source account)
curl -X POST -H "Content-Type: application/json" -d '{
    "time_ind": 1,
    "transac_type": "TRANSFER",
    "amount": 181.0,
    "src_bal": 181.0,
    "src_new_bal": 0.0,
    "dst_bal": 0.0,
    "dst_new_bal": 181.0
}' http://localhost:5001/predict
# Expected: {"is_fraud": 1}

# Test 2: Legitimate PAYMENT
curl -X POST -H "Content-Type: application/json" -d '{
    "time_ind": 1,
    "transac_type": "PAYMENT",
    "amount": 100.0,
    "src_bal": 1000.0,
    "src_new_bal": 900.0,
    "dst_bal": 0.0,
    "dst_new_bal": 0.0
}' http://localhost:5001/predict
# Expected: {"is_fraud": 0}
```

**View Stored Fraudulent Transactions:**
```bash
curl "http://localhost:5001/frauds?page=1&per_page=10"
# Expected: JSON with fraudulent_transactions array and pagination info
```

## 🐳 Complete Docker Deployment Guide

### Training Environment
```bash
# Start training environment
docker-compose -f docker-compose.training.yml up --build

# Access at: http://localhost:8888 (Token: fraud_detection_training)
# Complete the training, then stop:
docker-compose -f docker-compose.training.yml down
```

### Production API Stack
```bash
# Start complete API stack
docker-compose -f docker-compose.api.yml up --build

# Access services:
# - API: http://localhost:5001
# - Web UI: http://localhost:8501
# Stop when done:
docker-compose -f docker-compose.api.yml down
```

### Troubleshooting

**If API fails to start:**
1. Ensure training step completed successfully
2. Verify `model/fraud_model.joblib` exists (should be ~271KB)
3. Check Docker logs: `docker-compose -f docker-compose.api.yml logs`

**If ports are in use:**
```bash
# Check what's using the ports
lsof -i :8888 -i :5001 -i :8501
# Kill processes or change ports in docker-compose files
```

**Clean restart:**
```bash
# Remove all containers and rebuild
docker-compose -f docker-compose.training.yml down
docker-compose -f docker-compose.api.yml down
docker system prune -f
# Then restart the services
```
