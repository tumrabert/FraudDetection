import streamlit as st
import requests
import json
import pandas as pd
import os
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Fraud Detection API Tester",
    page_icon="🚨",
    layout="wide"
)

# Constants
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5002")  # Test API endpoint

# Title and description
st.title("🚨 Fraud Detection API Tester")
st.markdown("### Test the fraud detection machine learning model through a user-friendly interface")

# Sidebar for API configuration
st.sidebar.header("⚙️ Configuration")
api_url = st.sidebar.text_input("API Base URL", value=API_BASE_URL)

# Health check section
st.header("🩺 Health Check")
col1, col2 = st.columns([1, 3])

with col1:
    if st.button("Check API Health"):
        try:
            response = requests.get(f"{api_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                st.success("✅ API is healthy")
                st.json(health_data)
            else:
                st.error(f"❌ API health check failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection failed: {str(e)}")

# Transaction prediction section
st.header("💳 Transaction Fraud Prediction")

# Create tabs for different input methods
tab1, tab2 = st.tabs(["Manual Input", "Predefined Examples"])

with tab1:
    st.subheader("Enter Transaction Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        time_ind = st.number_input("Time Indicator (1-744)", min_value=1, max_value=744, value=1)
        transac_type = st.selectbox("Transaction Type", 
                                   ["PAYMENT", "TRANSFER", "CASH_OUT", "CASH_IN", "DEBIT"])
        amount = st.number_input("Amount", min_value=0.0, value=1000.0, format="%.2f")
    
    with col2:
        src_bal = st.number_input("Source Balance", min_value=0.0, value=10000.0, format="%.2f")
        src_new_bal = st.number_input("Source New Balance", min_value=0.0, value=9000.0, format="%.2f")
        dst_bal = st.number_input("Destination Balance", min_value=0.0, value=0.0, format="%.2f")
        dst_new_bal = st.number_input("Destination New Balance", min_value=0.0, value=0.0, format="%.2f")
    
    # Predict button
    if st.button("🔍 Predict Fraud", type="primary"):
        transaction_data = {
            "time_ind": time_ind,
            "transac_type": transac_type,
            "amount": amount,
            "src_bal": src_bal,
            "src_new_bal": src_new_bal,
            "dst_bal": dst_bal,
            "dst_new_bal": dst_new_bal
        }
        
        try:
            response = requests.post(f"{api_url}/predict", 
                                   json=transaction_data, 
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                is_fraud = result.get("is_fraud", 0)
                
                if is_fraud == 1:
                    st.error("🚨 **FRAUD DETECTED** - This transaction is flagged as fraudulent!")
                else:
                    st.success("✅ **LEGITIMATE** - This transaction appears to be legitimate.")
                
                # Show the prediction result
                st.json(result)
                
                # Show transaction details
                st.subheader("Transaction Details")
                df = pd.DataFrame([transaction_data])
                st.dataframe(df)
                
            else:
                st.error(f"Prediction failed: {response.status_code}")
                if response.text:
                    st.error(response.text)
                    
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")

with tab2:
    st.subheader("Test with Predefined Examples")
    
    # Predefined examples
    examples = {
        "Legitimate Payment": {
            "time_ind": 1,
            "transac_type": "PAYMENT",
            "amount": 9839.64,
            "src_bal": 170136.0,
            "src_new_bal": 160296.36,
            "dst_bal": 0.0,
            "dst_new_bal": 0.0
        },
        "Fraudulent Transfer": {
            "time_ind": 1,
            "transac_type": "TRANSFER",
            "amount": 181.0,
            "src_bal": 181.0,
            "src_new_bal": 0.0,
            "dst_bal": 0.0,
            "dst_new_bal": 0.0
        },
        "Large Cash Out": {
            "time_ind": 100,
            "transac_type": "CASH_OUT",
            "amount": 50000.0,
            "src_bal": 50000.0,
            "src_new_bal": 0.0,
            "dst_bal": 25000.0,
            "dst_new_bal": 0.0
        }
    }
    
    selected_example = st.selectbox("Choose an example:", list(examples.keys()))
    
    if st.button("🧪 Test Selected Example"):
        transaction_data = examples[selected_example]
        
        try:
            response = requests.post(f"{api_url}/predict", 
                                   json=transaction_data, 
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                is_fraud = result.get("is_fraud", 0)
                
                st.subheader(f"Result for: {selected_example}")
                
                if is_fraud == 1:
                    st.error("🚨 **FRAUD DETECTED**")
                else:
                    st.success("✅ **LEGITIMATE**")
                
                # Show transaction and result
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Transaction Data:**")
                    st.json(transaction_data)
                with col2:
                    st.write("**Prediction Result:**")
                    st.json(result)
                    
            else:
                st.error(f"Prediction failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")

# Flagged transactions section
st.header("📋 Flagged Fraudulent Transactions")

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    if st.button("🔄 Refresh Flagged Transactions"):
        try:
            response = requests.get(f"{api_url}/frauds", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if "fraudulent_transactions" in data:
                    # New paginated API response
                    transactions = data["fraudulent_transactions"]
                    pagination = data.get("pagination", {})
                    
                    if transactions:
                        st.success(f"Found {pagination.get('total_records', len(transactions))} flagged transactions")
                        
                        # Display pagination info
                        if pagination:
                            st.info(f"Page {pagination.get('current_page', 1)} of {pagination.get('total_pages', 1)} "
                                   f"({pagination.get('per_page', 20)} per page)")
                        
                        # Display transactions
                        df = pd.DataFrame(transactions)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No fraudulent transactions found.")
                        
                elif isinstance(data, list):
                    # Old direct list response (for backward compatibility)
                    if data:
                        st.success(f"Found {len(data)} flagged transactions")
                        df = pd.DataFrame(data)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No fraudulent transactions found.")
                else:
                    st.warning("Unexpected response format")
                    st.json(data)
                    
            else:
                st.error(f"Failed to fetch flagged transactions: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")

with col2:
    page_num = st.number_input("Page", min_value=1, value=1)

with col3:
    per_page = st.selectbox("Per Page", [10, 20, 50, 100], index=1)

if st.button("📄 Get Specific Page"):
    try:
        response = requests.get(f"{api_url}/frauds?page={page_num}&per_page={per_page}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            transactions = data.get("fraudulent_transactions", [])
            pagination = data.get("pagination", {})
            
            if transactions:
                st.success(f"Showing page {page_num}")
                st.info(f"Total records: {pagination.get('total_records', 0)} | "
                       f"Pages: {pagination.get('total_pages', 0)}")
                df = pd.DataFrame(transactions)
                st.dataframe(df, use_container_width=True)
            else:
                st.info(f"No transactions found on page {page_num}")
        else:
            st.error(f"Failed to fetch page: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("**Fraud Detection API Tester** | Built with Streamlit")
st.markdown("Test your fraud detection model with ease!")