import streamlit as st
import pandas as pd
import openai
import matplotlib.pyplot as plt

# Load OpenAI API Key from Streamlit Secrets
openai.api_key = st.secrets["Osk-proj-Vc4ZS9Q6RV6G4Q252l22MXfkpZwUnHlcoNG2iwe9PBv6y4zLdXN4klCTjFNBefENYQjBt-7XqtT3BlbkFJbo88EjucohIZPaOdg1saNGKnwl_C5IHxoY1A6XLVNySFXEV3NoXS6jZMuh-qy5qOyzWNIrZroAPENAI_API_KEY"]

# Load the dataset
@st.cache_data
def load_data():
    file_path = "Order Data (For Data Studio) - ShipFlex.csv"
    df = pd.read_csv(file_path)

    # Convert date columns to datetime
    date_columns = ["Order Date", "COMPLETED AT", "CANCELLED AT"]
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    return df

df = load_data()

# Function to process user queries using OpenAI API
def query_insights(user_query, df):
    """
    Uses OpenAI's GPT-4 to process queries related to order data.
    """
    context = f"""
    You are an AI assistant analyzing order data. The dataset contains order information with the following columns:
    {', '.join(df.columns)}.

    Here is a sample of the dataset:
    {df.head().to_string()}

    Based on this dataset, answer the following user query:
    {user_query}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data analyst providing insights on order data."},
                {"role": "user", "content": context}
            ],
            max_tokens=150
        )
        return response["choices"][0]["message"]["content"].strip()

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
