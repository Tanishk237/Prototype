def analyze_impact(df):
    """
    Calculates how much each review affects the overall rating.
    """

    base_rating = df["ai_rating"].mean()

    impacts = []

    for i in range(len(df)):
        temp_df = df.drop(df.index[i])

        new_rating = temp_df["ai_rating"].mean()

        impact_value = abs(base_rating - new_rating)

        impacts.append({
            "id": df.iloc[i]["id"],
            "review_text": df.iloc[i]["review_text"],
            "ai_rating": df.iloc[i]["ai_rating"],
            "sentiment": df.iloc[i]["sentiment"],
            "impact_score": round(impact_value, 5),
            "reasoning": df.iloc[i]["reasoning"]
        })

    # Sort by highest impact
    impacts_sorted = sorted(
        impacts,
        key=lambda x: x["impact_score"],
        reverse=True
    )

    return {
        "most_influential_reviews": impacts_sorted[:10],
        "least_influential_reviews": impacts_sorted[-10:]
    }
