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
    
    # Check if any reviews were successfully analyzed
    if not analysis_results:
        raise RuntimeError(
            "FATAL: No reviews were successfully analyzed.\n"
            "Possible causes:\n"
            "  1. LLM API is not accessible (check GROQ_API_KEY in .env)\n"
            "  2. LLM service is down\n"
            "  3. All review texts are empty or invalid\n"
            "Please check the error logs above and try again."
        )

    print("Aggregating results...")
    aggregation = aggregate_results(
        analysis_results,
        data["reviews"],
        data["ids"]
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
        "sentiment_stats": aggregation["sentiment_stats"],
        "ratings_dataframe": aggregation["ratings_dataframe"],
        "outliers": outliers,
        "impact_analysis": impacts,
        "all_reviews": df[["id", "review_text", "ai_rating", "sentiment", "reasoning"]].to_dict("records")
    }

    return final_output
