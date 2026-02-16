from src.modules.csv_loader import load_csv
from src.modules.review_analyzer import analyze_reviews
from src.modules.aggregation import aggregate_results
from src.modules.outlier_detection import detect_outliers
from src.modules.impact_analysis import analyze_impact


def run_pipeline(file_path):

    print("Loading CSV...")
    data = load_csv(file_path)

    print("Running LLM analysis...")
    analysis_results = analyze_reviews(
        data["reviews"],
        data["ids"]
    )

    print("Aggregating results...")
    aggregation = aggregate_results(
        analysis_results,
        data["reviews"]
    )

    df = aggregation["ratings_dataframe"]

    print("Detecting outliers...")
    outliers = detect_outliers(df)

    print("Analyzing impact...")
    impacts = analyze_impact(df)

    final_output = {
        "total_reviews": data["total_reviews"],
        "overall_ai_rating": aggregation["overall_ai_rating"],
        "weighted_rating": aggregation["weighted_rating"],
        "rating_stats": aggregation["rating_stats"],
        "sentiment_stats": aggregation["sentiment_stats"],
        "outliers": outliers,
        "impact_analysis": impacts,
        "all_reviews": df[["id", "review_text", "ai_rating", "sentiment", "reasoning"]].to_dict("records")
    }

    return final_output
