import streamlit as st
import pandas as pd
import tempfile

from src.pipeline import run_pipeline

st.set_page_config(
    page_title="AI Review Analyzer",
    layout="wide"
)

st.title("AI Review Analyzer")
st.caption("GenAI-powered review analysis with outliers & influence detection")

# Initialize session state for result caching
if "result" not in st.session_state:
    st.session_state.result = None

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(uploaded_file.getvalue())
        file_path = tmp.name

    if st.button("Run Analysis"):
        with st.spinner("Analyzing reviews using AI..."):
            result = run_pipeline(file_path)
        
        # Store result in session state for dropdown to access
        st.session_state.result = result

        st.success("Analysis completed")

    # Show metrics if result is available
    if st.session_state.result:
        result = st.session_state.result
        
        # -------------------------------
        # SUMMARY METRICS
        # -------------------------------
        st.header("Overall Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric("Overall AI Rating", result["overall_ai_rating"])
        col2.metric("Weighted Rating", result["weighted_rating"])
        col3.metric(
            "Overall Sentiment",
            round(result["sentiment_stats"]["mean_sentiment"], 2)
        )

        # -------------------------------
        # SIMPLE & CLEAR GRAPHS
        # -------------------------------
        st.header("Rating & Sentiment Overview")

        df_all = pd.DataFrame(result["impact_analysis"]["most_influential_reviews"])
        full_df = result["outliers"]["statistical_outliers"]

        ratings_df = pd.DataFrame(result["outliers"]["strong_positive_reviews"] +
                                  result["outliers"]["strong_negative_reviews"])

        # Rating Distribution
        st.subheader("Rating Distribution")
        all_reviews_df = pd.DataFrame(result["all_reviews"])
        rating_counts = pd.DataFrame(
            pd.Series(all_reviews_df["ai_rating"]).value_counts().sort_index()
        ).rename(columns={0: "count"})

        st.bar_chart(rating_counts)

        # Sentiment Distribution with proper Neutral category
        st.subheader("Sentiment Distribution")
        # Bin sentiments into 5 categories with proper boundaries
        sentiment_bins = pd.cut(
            all_reviews_df["sentiment"],
            bins=[-1.0, -0.5, -0.1, 0.1, 0.5, 1.0],
            labels=["Very Negative", "Negative", "Neutral", "Positive", "Very Positive"],
            include_lowest=True
        ).value_counts().sort_index()

        st.bar_chart(sentiment_bins)

        # Count summary
        total_count = result["total_reviews"]
        outliers_count = result["outliers"]["counts"]["statistical_outliers"]
        strong_neg = result["outliers"]["counts"]["strong_negative"]
        strong_pos = result["outliers"]["counts"]["strong_positive"]
        neutral_count = result["outliers"]["counts"]["neutral_balanced"]
        influential = len(result["impact_analysis"]["most_influential_reviews"])
        
        st.subheader("📊 Review Category Breakdown")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Reviews", total_count)
        col2.metric("Strong Negative", strong_neg)
        col3.metric("Neutral/Balanced", neutral_count)
        col4.metric("Strong Positive", strong_pos)
        col5.metric("Most Influential", influential)

        # -------------------------------
        # 🔍 REVIEW EXPLORER
        # -------------------------------
        st.header("🔍 Review Explorer")

        review_category = st.selectbox(
            "Select review category",
            [
                "Strong Negative Reviews",
                "Neutral/Balanced Reviews",
                "Strong Positive Reviews",
                "Statistical Outliers",
                "Most Influential Reviews"
            ],
            key="review_category_select"
        )

        if review_category == "Strong Negative Reviews":
            review_data = result["outliers"]["strong_negative_reviews"]

        elif review_category == "Neutral/Balanced Reviews":
            review_data = result["outliers"]["neutral_reviews"]

        elif review_category == "Strong Positive Reviews":
            review_data = result["outliers"]["strong_positive_reviews"]

        elif review_category == "Statistical Outliers":
            review_data = result["outliers"]["statistical_outliers"]

        else:
            review_data = result["impact_analysis"]["most_influential_reviews"]

        if len(review_data) == 0:
            st.info("No reviews found for this category.")
        else:
            df_reviews = pd.DataFrame(review_data)

            selected_review = st.selectbox(
                "Choose a review",
                df_reviews.index,
                format_func=lambda i: f"ID {df_reviews.loc[i, 'id']} | Rating {df_reviews.loc[i, 'ai_rating']}",
                key="review_detail_select"
            )

            review = df_reviews.loc[selected_review]

            st.markdown("### Review Details")

            st.write("**Review Text:**")
            st.info(review["review_text"])

            col1, col2, col3 = st.columns(3)
            col1.metric("AI Rating", review["ai_rating"])
            col2.metric("Sentiment", review["sentiment"])
            if "impact_score" in review:
                col3.metric("Impact Score", review["impact_score"])

            st.write("**AI Reasoning:**")
            st.write(review["reasoning"])
