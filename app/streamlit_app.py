import streamlit as st
import pandas as pd
import altair as alt
import tempfile

from src.pipeline import run_pipeline

st.set_page_config(page_title="AI Review Analyzer", layout="wide")
st.title("AI Review Analyzer")
st.caption("GenAI-powered review analysis with consistent analytics")

if "result" not in st.session_state:
    st.session_state.result = None

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(uploaded_file.getvalue())
        file_path = tmp.name

    if st.button("Run Analysis"):
        with st.spinner("Analyzing reviews using AI..."):
            st.session_state.result = run_pipeline(file_path)
        st.success("Analysis completed")

if st.session_state.result:
    result = st.session_state.result
    df_all = pd.DataFrame(result["ratings_dataframe"])

    st.header("Overall Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall AI Rating", round(result["overall_ai_rating"], 2))
    col2.metric("Weighted Rating", round(result["weighted_rating"], 2))
    col3.metric("Mean Sentiment", round(result["sentiment_stats"]["mean_sentiment"], 3))

    st.subheader("Rating Distribution")
    rating_counts = (
        df_all["ai_rating"]
        .value_counts()
        .sort_index()
        .reset_index()
    )
    rating_counts.columns = ["ai_rating", "count"]
    rating_chart = (
        alt.Chart(rating_counts)
        .mark_bar(color="#4C78A8")
        .encode(
            x=alt.X("ai_rating:O", title="AI Rating"),
            y=alt.Y("count:Q", title="Count"),
            tooltip=["ai_rating", "count"]
        )
        .properties(height=300)
    )
    st.altair_chart(rating_chart, use_container_width=True)

    st.subheader("Sentiment Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Min Sentiment", f"{df_all['sentiment'].min():.3f}")
    col2.metric("Mean Sentiment", f"{df_all['sentiment'].mean():.3f}")
    col3.metric("Max Sentiment", f"{df_all['sentiment'].max():.3f}")
    col4.metric("Std Dev", f"{df_all['sentiment'].std():.3f}")

    st.subheader("Sentiment Categories")
    sentiment_counts = (
        df_all["sentiment_category"]
        .value_counts()
        .reindex(["Strong Negative", "Negative", "Neutral", "Positive", "Strong Positive"], fill_value=0)
        .reset_index()
    )
    sentiment_counts.columns = ["sentiment_category", "count"]
    sentiment_chart = (
        alt.Chart(sentiment_counts)
        .mark_bar(color="#F58518")
        .encode(
            x=alt.X("sentiment_category:N", title="Sentiment", sort=["Strong Negative", "Negative", "Neutral", "Positive", "Strong Positive"]),
            y=alt.Y("count:Q", title="Count"),
            tooltip=["sentiment_category", "count"]
        )
        .properties(height=300)
    )
    st.altair_chart(sentiment_chart, use_container_width=True)

    st.subheader("Review Category Breakdown")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Reviews", len(df_all))
    col2.metric("Strong Negative", (df_all["sentiment_category"] == "Strong Negative").sum())
    col3.metric("Neutral / Balanced", (df_all["sentiment_category"] == "Neutral").sum())
    col4.metric("Strong Positive", (df_all["sentiment_category"] == "Strong Positive").sum())
    col5.metric("Most Influential", len(result["impact_analysis"]["most_influential_reviews"]))

    st.header("Review Explorer")
    review_category = st.selectbox(
        "Select review category",
        ["Strong Negative Reviews", "Neutral/Balanced Reviews", "Strong Positive Reviews", "Statistical Outliers", "Most Influential Reviews"]
    )

    if review_category == "Strong Negative Reviews":
        df_reviews = df_all[df_all["sentiment_category"] == "Strong Negative"]
    elif review_category == "Neutral/Balanced Reviews":
        df_reviews = df_all[df_all["sentiment_category"] == "Neutral"]
    elif review_category == "Strong Positive Reviews":
        df_reviews = df_all[df_all["sentiment_category"] == "Strong Positive"]
    elif review_category == "Statistical Outliers":
        df_reviews = pd.DataFrame(result["outliers"]["statistical_outliers"])
    else:
        df_reviews = pd.DataFrame(result["impact_analysis"]["most_influential_reviews"])

    if df_reviews.empty:
        st.info("No reviews found for this category.")
    else:
        selected_index = st.selectbox("Choose a review", df_reviews.index, format_func=lambda i: f"ID {df_reviews.loc[i, 'id']} | Rating {df_reviews.loc[i, 'ai_rating']}")
        review = df_reviews.loc[selected_index]
        st.markdown("### Review Details")
        st.info(review["review_text"])
        col1, col2, col3 = st.columns(3)
        col1.metric("AI Rating", review["ai_rating"])
        col2.metric("Sentiment", review["sentiment"])
        if "impact_score" in review:
            col3.metric("Impact Score", review["impact_score"])
        st.markdown("**AI Reasoning:**")
        st.write(review["reasoning"])