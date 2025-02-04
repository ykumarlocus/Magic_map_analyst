import streamlit as st
import pandas as pd
import openai
import matplotlib.pyplot as plt

# Load OpenAI API Key from Streamlit Secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Load the dataset
@st.cache_data
def load_data():
    file_path = "Order Data (For Data Studio) - ShipFlex.csv"
    
    try:
        df = pd.read_csv(file_path)

        # Convert date columns to datetime if they exist
        date_columns = ["Order Date", "COMPLETED AT", "CANCELLED AT"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return pd.DataFrame()  # Return empty DataFrame if loading fails

df = load_data()

# Function to process user queries using OpenAI API, with real data calculations
def query_insights(user_query, df):
    """
    Uses OpenAI's GPT-4 to provide real insights based on calculated values.
    """
    if df.empty:
        return "Error: No data loaded. Please check if the dataset is available."

    # Precompute key statistics from the dataset
    total_orders = df.shape[0]
    completed_orders = df[df["Terminal STATUS"] == "COMPLETED"].shape[0] if "Terminal STATUS" in df.columns else "N/A"
    cancelled_orders = df[df["Terminal STATUS"] == "CANCELLED"].shape[0] if "Terminal STATUS" in df.columns else "N/A"

    top_city = df["CITY"].value_counts().idxmax() if "CITY" in df.columns else "N/A"
    top_state = df["STATE"].value_counts().idxmax() if "STATE" in df.columns else "N/A"

    common_cancellation_reason = df["Cancellation REASON DESCRIPTION"].value_counts().idxmax() if "Cancellation REASON DESCRIPTION" in df.columns else "N/A"

    # Create a context summary with real computed values
    context = f"""
    You are an AI assistant analyzing order data. Based on the dataset provided:

    - Total Orders: {total_orders}
    - Completed Orders: {completed_orders}
    - Cancelled Orders: {cancelled_orders}
    - Top City for Orders: {top_city}
    - Top State for Orders: {top_state}
    - Most Common Cancellation Reason: {common_cancellation_reason}

    User Question: {user_query}

    Provide a helpful, natural language response based on the above data. Format the response like a human-written answer.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data analyst providing insights on order data."},
                {"role": "user", "content": context}
            ]
        )
        return response['choices'][0]['message']['content'].strip()

    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.title("📊 AI-Powered Order Insights")
st.write("Ask a question about your order data, and I'll provide AI-generated insights!")

user_query = st.text_input("Type your question here:", "")

if st.button("Get Answer"):
    if user_query:
        result = query_insights(user_query, df)
        st.write(result)
    else:
        st.write("Please enter a valid question.")
