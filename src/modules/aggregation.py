import pandas as pd


def aggregate_results(analysis_results, original_reviews):
    """
    Aggregates LLM review analysis into overall metrics.
    """

    df = pd.DataFrame(analysis_results)
    df["review_text"] = original_reviews

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

    # Additional statistics (very useful for analytics)
    rating_stats = {
        "mean": round(df["ai_rating"].mean(), 3),
        "median": round(df["ai_rating"].median(), 3),
        "std_dev": round(df["ai_rating"].std(), 3),
        "min": round(df["ai_rating"].min(), 3),
        "max": round(df["ai_rating"].max(), 3)
    }

    sentiment_stats = {
        "mean_sentiment": round(df["sentiment"].mean(), 3),
        "std_sentiment": round(df["sentiment"].std(), 3)
    }

    return {
        "overall_ai_rating": round(overall_ai_rating, 3),
        "weighted_rating": round(weighted_rating, 3),
        "rating_stats": rating_stats,
        "sentiment_stats": sentiment_stats,
        "ratings_dataframe": df
    }
