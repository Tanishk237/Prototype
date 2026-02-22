import pandas as pd


def aggregate_results(analysis_results, original_reviews, original_ids=None):
    """
    Aggregates LLM review analysis into overall metrics.
    """

    if not analysis_results:
        raise ValueError(
            "No reviews were successfully analyzed by the LLM. "
            "This could indicate: API connectivity issues, LLM failures, "
            "or malformed review data. Check the logs above for details."
        )

    df = pd.DataFrame(analysis_results)
    df["sentiment_category"] = df["sentiment"].apply(categorize_sentiment)


    # Attach the original review text by matching IDs when possible.
    # `original_ids` is expected to be the list of ids aligned with `original_reviews`.
    if original_ids is not None and len(original_ids) == len(original_reviews):
        id_to_text = {i: t for i, t in zip(original_ids, original_reviews)}
        df["review_text"] = df["id"].map(id_to_text)
    else:
        # Fallback: use first N reviews (preserves previous behavior)
        df["review_text"] = original_reviews[:len(df)]

    # Basic overall average rating
    overall_ai_rating = df["ai_rating"].mean()

    # Sentiment-weighted rating (stronger opinions weigh more)
    sentiment_weights = df["sentiment"].abs()

    if sentiment_weights.sum() == 0:
        weighted_rating = overall_ai_rating
    else:
        weighted_rating = (
            (df["ai_rating"] * sentiment_weights).sum()
            / sentiment_weights.sum()
        )

    # Additional statistics
    sentiment_stats = {
        "mean_sentiment": round(df["sentiment"].mean()),
        "std_sentiment": round(df["sentiment"].std())
    }

    return {
        "overall_ai_rating": round(overall_ai_rating),
        "weighted_rating": round(weighted_rating),
        "sentiment_stats": sentiment_stats,
        "ratings_dataframe": df
    }
def categorize_sentiment(score: float) -> str:
    if score <= -0.6:
        return "Strong Negative"
    elif score < -0.2:
        return "Negative"
    elif score <= 0.2:
        return "Neutral"
    elif score < 0.6:
        return "Positive"
    else:
        return "Strong Positive"
