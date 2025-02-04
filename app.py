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

        # Ensure column names are stripped of whitespace issues
        df.columns = df.columns.str.strip()

        # Convert date columns to datetime if they exist
        date_columns = [
            "Order Date", "COMPLETED AT", "CANCELLED AT", "RETURN COMPLETED AT", 
            "IN TRANSIT AT", "PICKED UP AT"
        ]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return pd.DataFrame()  # Return empty DataFrame if loading fails

df = load_data()

# Function to compute responses for common queries
def compute_answer(user_query, df):
    try:
        # Convert user query to lowercase for case-insensitive matching
        user_query = user_query.lower()

        if "how many orders were completed" in user_query:
            result = df[df["Terminal STATUS"] == "COMPLETED"].shape[0]

        elif "how many orders were canceled" in user_query:
            result = df[df["Terminal STATUS"] == "CANCELLED"].shape[0]

        elif "how many orders were returned" in user_query:
            result = df[df["Terminal STATUS"] == "RETURN_COMPLETED"].shape[0]

        elif "which city has the most canceled orders" in user_query:
            if "CITY" in df.columns and "Terminal STATUS" in df.columns:
                city_cancel_counts = df[df["Terminal STATUS"] == "CANCELLED"]["CITY"].value_counts()
                result = city_cancel_counts.idxmax() if not city_cancel_counts.empty else "No cancellations found."
            else:
                result = "Required data columns are missing in the dataset."

        elif "which state has the most canceled orders" in user_query:
            if "STATE" in df.columns and "Terminal STATUS" in df.columns:
                state_cancel_counts = df[df["Terminal STATUS"] == "CANCELLED"]["STATE"].value_counts()
                result = state_cancel_counts.idxmax() if not state_cancel_counts.empty else "No cancellations found."
            else:
                result = "Required data columns are missing in the dataset."

        elif "trend of order cancellations over time" in user_query:
            if "CANCELLED AT" in df.columns and "Terminal STATUS" in df.columns:
                cancel_trend = df[df["Terminal STATUS"] == "CANCELLED"].groupby(df["CANCELLED AT"].dt.date).size()
                
                if cancel_trend.empty:
                    return "No cancellation data available for trend analysis."

                plt.figure(figsize=(10, 5))
                plt.plot(cancel_trend.index, cancel_trend.values, marker="o", linestyle="-")
                plt.xlabel("Date")
                plt.ylabel("Number of Cancellations")
                plt.title("Order Cancellations Over Time")
                st.pyplot(plt)
                return "Displayed the trend of order cancellations over time."
            else:
                result = "Required data columns are missing in the dataset."

        elif "average time between order placement and pickup" in user_query:
            if "PICKUP REACHED AT" in df.columns and "Order Date" in df.columns:
                df["pickup_time"] = (df["PICKUP REACHED AT"] - df["Order Date"]).dt.total_seconds() / 3600
                result = round(df["pickup_time"].mean(), 2)
            else:
                result = "Required data columns are missing in the dataset."

        else:
            result = "Sorry, I couldn't find a direct answer. Try rewording your question."

        return result
    except Exception as e:
        return f"Error in computation: {str(e)}"

# Function to get human-like explanations via OpenAI
def explain_result(user_query, result):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data analyst explaining insights in simple terms."},
                {"role": "user", "content": f"The result for '{user_query}' is: {result}. Please explain this in simple words."}
            ]
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error in AI explanation: {str(e)}"

# Streamlit UI
st.title("📊 AI-Powered Order Insights")
st.write("Ask a question about your order data, and I'll provide AI-generated insights with step-by-step calculations!")

user_query = st.text_input("Type your question here:", "")

if st.button("Get Answer"):
    if user_query:
        st.subheader("🔍 Understanding Your Question")
        st.write(f"User Query: **{user_query}**")

        # Compute Answer
        computed_result = compute_answer(user_query, df)

        # Get Human Explanation via OpenAI
        explanation = explain_result(user_query, computed_result)

        st.subheader("✅ Final Answer in Natural Language")
        st.write(explanation)
    else:
        st.write("Please enter a valid question.")
