#!/bin/bash

# Function to handle shutdown
cleanup() {
    echo "Stopping all services..."
    kill $FLASK_PID $STREAMLIT_PID $JUPYTER_PID 2>/dev/null
    exit 0
}

# Set trap to handle shutdown signals
trap cleanup SIGTERM SIGINT

echo "Starting Fraud Detection Services..."

# Start Flask API in background
echo "Starting Flask API on port 5000..."
python app.py &
FLASK_PID=$!

# Start Streamlit UI in background
echo "Starting Streamlit UI on port 8501..."
streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=8501 &
STREAMLIT_PID=$!

# Start Jupyter Lab in background (always on)
echo "Starting Jupyter Lab on port 8888..."
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=fraud_detection_training &
JUPYTER_PID=$!

echo "All services started!"
echo "- API: http://localhost:5000"
echo "- Streamlit: http://localhost:8501"
echo "- Jupyter: http://localhost:8888 (token: fraud_detection_training)"

# Wait for all background processes
wait