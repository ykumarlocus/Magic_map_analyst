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
        if "how many orders were completed" in user_query.lower():
            result = df[df["Terminal STATUS"] == "COMPLETED"].shape[0]

        elif "how many orders were canceled" in user_query.lower():
            result = df[df["Terminal STATUS"] == "CANCELLED"].shape[0]

        elif "how many orders were returned" in user_query.lower():
            result = df[df["Terminal STATUS"] == "RETURN_COMPLETED"].shape[0]

        elif "percentage of orders delivered on time" in user_query.lower():
            total_deliveries = df[df["Terminal STATUS"] == "COMPLETED"].shape[0]
            on_time_deliveries = df[df["SLA Compliance"] == "ON_TIME"].shape[0]
            result = round((on_time_deliveries / total_deliveries) * 100, 2) if total_deliveries else 0

        elif "percentage of orders delivered late" in user_query.lower():
            total_deliveries = df[df["Terminal STATUS"] == "COMPLETED"].shape[0]
            late_deliveries = df[df["SLA Compliance"] == "LATE"].shape[0]
            result = round((late_deliveries / total_deliveries) * 100, 2) if total_deliveries else 0

        elif "city with the highest number of completed orders" in user_query.lower():
            result = df[df["Terminal STATUS"] == "COMPLETED"]["CITY"].value_counts().idxmax()

        elif "state with the highest number of completed orders" in user_query.lower():
            result = df[df["Terminal STATUS"] == "COMPLETED"]["STATE"].value_counts().idxmax()

        elif "average time taken for order completion" in user_query.lower():
            df["completion_time"] = (df["COMPLETED AT"] - df["Order Date"]).dt.total_seconds() / 3600
            result = round(df["completion_time"].mean(), 2)

        elif "orders were delayed" in user_query.lower():
            delayed_orders = df[df["SLA Compliance"] == "LATE"]
            result = delayed_orders[["ORDER ID", "Order Date", "COMPLETED AT"]]

        elif "top reasons for order cancellations" in user_query.lower():
            result = df["Cancellation REASON DESCRIPTION"].value_counts().head(5)

        elif "which teams have the highest cancellation rates" in user_query.lower():
            result = df[df["Terminal STATUS"] == "CANCELLED"]["TEAM NAME"].value_counts().head(5)

        elif "average weight of completed orders" in user_query.lower():
            result = df[df["Terminal STATUS"] == "COMPLETED"]["WEIGHT VALUE"].mean()

        elif "average weight of canceled orders" in user_query.lower():
            result = df[df["Terminal STATUS"] == "CANCELLED"]["WEIGHT VALUE"].mean()

        elif "which carrier handles the heaviest orders" in user_query.lower():
            result = df.groupby("CARRIER NAME")["WEIGHT VALUE"].mean().idxmax()

        elif "trend of order cancellations over time" in user_query.lower():
            cancel_trend = df.groupby(df["CANCELLED AT"].dt.date).size()
            plt.figure(figsize=(10, 5))
            plt.plot(cancel_trend.index, cancel_trend.values, marker="o", linestyle="-")
            plt.xlabel("Date")
            plt.ylabel("Number of Cancellations")
            plt.title("Order Cancellations Over Time")
            st.pyplot(plt)
            return "Displayed the trend of order cancellations over time."

        elif "average time between order placement and pickup" in user_query.lower():
            df["pickup_time"] = (df["PICKUP REACHED AT"] - df["Order Date"]).dt.total_seconds() / 3600
            result = round(df["pickup_time"].mean(), 2)

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

        st.subheader("✅ Your Answer")
        st.write(explanation)
    else:
        st.write("Please enter a valid question.")
