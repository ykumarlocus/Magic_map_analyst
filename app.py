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

# Function to process user queries using OpenAI API
def query_insights(user_query, df):
    """
    Uses OpenAI's GPT-4 to process queries related to order data.
    """
    if df.empty:
        return "Error: No data loaded. Please check if the dataset is available."

    context = f"""
    You are an AI assistant analyzing order data. The dataset contains order information with the following columns:
    {', '.join(df.columns)}.

    Here is a small sample of the dataset:
    {df.head(5).to_string()}

    The user has asked the following question:
    {user_query}

    Please answer based on the dataset, and if necessary, suggest calculations or insights.
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
