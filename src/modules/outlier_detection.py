def detect_outliers(df):
    """
    Detect outliers using percentile-based extremes.
    This guarantees only truly extreme ratings are flagged.
    """

    # Percentile thresholds
    low_cut = df["ai_rating"].quantile(0.05)
    high_cut = df["ai_rating"].quantile(0.95)

    # Semantic safety bounds
    semantic_low = 2.0
    semantic_high = 4.5

    statistical_outliers = df[
        (df["ai_rating"] <= max(low_cut, semantic_low)) |
        (df["ai_rating"] >= min(high_cut, semantic_high))
    ]

    # Sentiment buckets
    strong_negative = df[df["sentiment"] <= -0.7]
    strong_positive = df[df["sentiment"] >= 0.7]
    neutral_balanced = df[
        (df["sentiment"] > -0.3) & (df["sentiment"] < 0.3)
    ]

    return {
        "percentile_bounds": {
            "low_5_percentile": round(low_cut, 2),
            "high_95_percentile": round(high_cut, 2),
        },

        "statistical_outliers": statistical_outliers[
            ["id", "review_text", "ai_rating", "sentiment", "reasoning"]
        ].to_dict("records"),

        "strong_negative_reviews": strong_negative[
            ["id", "review_text", "ai_rating", "sentiment", "reasoning"]
        ].to_dict("records"),

        "strong_positive_reviews": strong_positive[
            ["id", "review_text", "ai_rating", "sentiment", "reasoning"]
        ].to_dict("records"),

        "neutral_reviews": neutral_balanced[
            ["id", "review_text", "ai_rating", "sentiment", "reasoning"]
        ].to_dict("records"),

        "counts": {
            "statistical_outliers": len(statistical_outliers),
            "strong_negative": len(strong_negative),
            "strong_positive": len(strong_positive),
            "neutral_balanced": len(neutral_balanced)
        }
    }
def detect_outliers(df):
    """
    Detect outliers using percentile-based extremes.
    This guarantees only truly extreme ratings are flagged.
    """

    # -------------------------------
    # PERCENTILE THRESHOLDS
    # -------------------------------
    low_cut = df["ai_rating"].quantile(0.05)
    high_cut = df["ai_rating"].quantile(0.95)

    # Semantic safety (absolute bounds)
    semantic_low = 2.0
    semantic_high = 4.5

    statistical_outliers = df[
        (df["ai_rating"] <= max(low_cut, semantic_low)) |
        (df["ai_rating"] >= min(high_cut, semantic_high))
    ]

    # -------------------------------
    # SENTIMENT BUCKETS
    # -------------------------------
    strong_negative = df[df["sentiment"] <= -0.7]
    strong_positive = df[df["sentiment"] >= 0.7]
    neutral_balanced = df[
        (df["sentiment"] > -0.3) & (df["sentiment"] < 0.3)
    ]

    return {
        "percentile_bounds": {
            "low_5_percentile": round(low_cut, 2),
            "high_95_percentile": round(high_cut, 2),
            "semantic_low": semantic_low,
            "semantic_high": semantic_high
        },

        "statistical_outliers": statistical_outliers[
            ["id", "review_text", "ai_rating", "sentiment", "reasoning"]
        ].to_dict("records"),

        "strong_negative_reviews": strong_negative[
            ["id", "review_text", "ai_rating", "sentiment", "reasoning"]
        ].to_dict("records"),

        "strong_positive_reviews": strong_positive[
            ["id", "review_text", "ai_rating", "sentiment", "reasoning"]
        ].to_dict("records"),

        "neutral_reviews": neutral_balanced[
            ["id", "review_text", "ai_rating", "sentiment", "reasoning"]
        ].to_dict("records"),

        "counts": {
            "statistical_outliers": len(statistical_outliers),
            "strong_negative": len(strong_negative),
            "strong_positive": len(strong_positive),
            "neutral_balanced": len(neutral_balanced)
        }
    }