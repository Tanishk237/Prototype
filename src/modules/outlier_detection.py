def detect_outliers(df):
    """
    Detect outliers using IQR (robust to skewed data).
    """

    q1 = df["ai_rating"].quantile(0.25)
    q3 = df["ai_rating"].quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    statistical_outliers = df[
        (df["ai_rating"] < lower_bound) |
        (df["ai_rating"] > upper_bound)
    ]

    strong_negative = df[df["sentiment"] <= -0.5]
    strong_positive = df[df["sentiment"] >= 0.5]
    neutral_balanced = df[(df["sentiment"] > -0.5) & (df["sentiment"] < 0.5)]

    return {
        "iqr_bounds": {
            "lower": round(lower_bound, 2),
            "upper": round(upper_bound, 2),
            "q1": round(q1, 2),
            "q3": round(q3, 2)
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
