def compute_answer(user_query, df):
    try:
        # Ensure column names match exactly
        if "how many orders were completed" in user_query.lower():
            result = df[df["Terminal STATUS"] == "COMPLETED"].shape[0]

        elif "how many orders were canceled" in user_query.lower():
            result = df[df["Terminal STATUS"] == "CANCELLED"].shape[0]

        elif "which city has the most canceled orders" in user_query.lower():
            city_cancel_counts = df[df["Terminal STATUS"] == "CANCELLED"]["CITY"].value_counts()
            result = city_cancel_counts.idxmax() if not city_cancel_counts.empty else "No cancellations found."

        elif "which state has the most canceled orders" in user_query.lower():
            state_cancel_counts = df[df["Terminal STATUS"] == "CANCELLED"]["STATE"].value_counts()
            result = state_cancel_counts.idxmax() if not state_cancel_counts.empty else "No cancellations found."

        elif "trend of order cancellations over time" in user_query.lower():
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
            result = "Sorry, I couldn't find a direct answer. Try rewording your question."

        return result
    except Exception as e:
        return f"Error in computation: {str(e)}"
