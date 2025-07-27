import sqlite3
import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize Flask App
app = Flask(__name__)

# --- DATABASE SETUP ---
def init_db():
    """Initializes the SQLite database and creates the table if it doesn't exist."""
    conn = sqlite3.connect('fraud_predictions.db')
    cursor = conn.cursor()
    # Create table with columns matching the transaction data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time_ind INTEGER,
            transac_type TEXT,
            amount REAL,
            src_bal REAL,
            src_new_bal REAL,
            dst_bal REAL,
            dst_new_bal REAL
        )
    ''')
    conn.commit()
    conn.close()

# --- LOAD MODEL ---
# Load the pre-trained model pipeline
try:
    model = joblib.load('model/fraud_model.joblib')
    print("Model loaded successfully.")
except FileNotFoundError:
    print("Error: Model file not found. Make sure 'fraud_model.joblib' is in the 'model/' directory.")
    model = None

# --- API ENDPOINTS ---

@app.route('/predict', methods=['POST'])
def predict_fraud():
    """Accepts a transaction in JSON and returns a fraud prediction."""
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    # Get the JSON data from the request [cite: 35]
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    # Calculate engineered features as done in training
    data['error_bal_src'] = data.get('src_bal', 0) - data.get('amount', 0) - data.get('src_new_bal', 0)
    data['error_bal_dst'] = data.get('dst_bal', 0) + data.get('amount', 0) - data.get('dst_new_bal', 0)
    
    # Convert the JSON data into a pandas DataFrame
    # This matches the format used for training
    df = pd.DataFrame([data])

    # Make a prediction
    try:
        prediction = model.predict(df)[0]
        is_fraud = int(prediction) # Convert numpy int to standard Python int
    except Exception as e:
        return jsonify({"error": f"Prediction error: {str(e)}"}), 500
        
    # If fraud is detected, store the transaction in the database [cite: 41]
    if is_fraud == 1:
        try:
            conn = sqlite3.connect('fraud_predictions.db')
            cursor = conn.cursor()
            # Insert transaction data into database
            cursor.execute('''
                INSERT INTO predictions (time_ind, transac_type, amount, src_bal, src_new_bal, dst_bal, dst_new_bal)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('time_ind'), data.get('transac_type'), data.get('amount'),
                data.get('src_bal'), data.get('src_new_bal'), data.get('dst_bal'),
                data.get('dst_new_bal')
            ))
            conn.commit()
            conn.close()
        except Exception as e:
             return jsonify({"error": f"Database error: {str(e)}"}), 500

    # Return the prediction result as JSON [cite: 35]
    return jsonify({"is_fraud": is_fraud})

@app.route('/frauds', methods=['GET'])
def get_frauds():
    """Returns transactions previously predicted as fraudulent with pagination."""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page
        
        conn = sqlite3.connect('fraud_predictions.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as total FROM predictions")
        total = cursor.fetchone()['total']
        
        # Fetch paginated records
        cursor.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT ? OFFSET ?", (per_page, offset))
        rows = cursor.fetchall()
        conn.close()
        
        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        
        return jsonify({
            "fraudulent_transactions": [dict(row) for row in rows],
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total_records": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API is running and model is loaded."""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None
    })

# --- MAIN ---
if __name__ == '__main__':
    # Initialize the database when the app starts
    init_db()
    # Run the Flask app
    app.run(debug=True, port=5000, host='0.0.0.0')
