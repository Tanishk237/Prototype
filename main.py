from src.pipeline import run_pipeline
import json


if __name__ == "__main__":

    result = run_pipeline("data/input/reviews.csv")

    print("\nFINAL SUMMARY\n")
    print("Total Reviews:", result["total_reviews"])
    print("Overall AI Rating:", result["overall_ai_rating"])
    print("Weighted Rating:", result["weighted_rating"])

    print("\nTop 3 Influential Reviews:")
    for r in result["impact_analysis"]["most_influential_reviews"][:3]:
        print(r)

    print("\nOutlier Counts:")
    print(result["outliers"]["counts"])
