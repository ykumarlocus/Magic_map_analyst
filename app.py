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
        date_columns = ["Order Date", "COMPLETED AT", "CANCELLED AT", "RETURN COMPLETED AT", "IN TRANSIT AT", "PICKED UP AT"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return pd.DataFrame()  # Return empty DataFrame if loading fails

df = load_data()

# Function to convert user query into Python calculations
def generate_python_code(user_query, df):
    """
    Uses OpenAI API to convert the user query into a Python calculation.
    """
    context = f"""
    You are a Python expert. Convert the following user query into a Python function
    that can process the given order dataset.

    Dataset Columns:
    {', '.join(df.columns)}

    Sample Data:
    {df.head(5).to_string()}

    User Query:
    {user_query}

    Output a Python function that calculates the answer based on Pandas.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Python data expert who writes optimized Pandas queries."},
                {"role": "user", "content": context}
            ]
        )
        python_code = response['choices'][0]['message']['content'].strip()
        return python_code
    except Exception as e:
        return f"Error: {str(e)}"

# Function to execute the generated Python code
def execute_python_code(code, df):
    """
    Executes the generated Python code to get the result.
    """
    try:
        exec_globals = {"df": df}
        exec(code, exec_globals)
        result = exec_globals.get("result", "No result variable found.")
        return result
    except Exception as e:
        return f"Execution Error: {str(e)}"

# Streamlit UI
st.title("📊 AI-Powered Order Insights")
st.write("Ask a question about your order data, and I'll provide AI-generated insights with step-by-step calculations!")

user_query = st.text_input("Type your question here:", "")

if st.button("Get Answer"):
    if user_query:
        st.subheader("🔍 Understanding Your Question")
        st.write(f"User Query: **{user_query}**")

        # Generate Python code
        python_code = generate_python_code(user_query, df)

        st.subheader("📝 Generated Python Code")
        st.code(python_code, language="python")

        # Execute the generated code
        result = execute_python_code(python_code, df)

        st.subheader("📊 Calculation & Data Used")
        st.write("Here is the data that was used to generate this response:")
        st.write(df.head())

        st.subheader("✅ Final Answer in Natural Language")
        st.write(result)
    else:
        st.write("Please enter a valid question.")
