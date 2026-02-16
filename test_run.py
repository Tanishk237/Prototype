from pathlib import Path
from src.utils.llm_utils import get_llm
from src.modules.csv_loader import load_csv
from src.modules.review_analyzer import analyze_reviews
from src.modules.aggregation import aggregate_results
from src.modules.outlier_detection import detect_outliers
from src.modules.impact_analysis import analyze_impact

print("\n--- TEST 1: Checking LLM Connection ---")

llm = get_llm()
response = llm.invoke("Say hello in one line")

print("Model Response:", response)


print("\n--- TEST 2: Loading CSV ---")

data = load_csv("data/input/reviews.csv")

print("Total Reviews Found:", data["total_reviews"])
print("First Review:", data["reviews"][0])


print("\n--- TEST 3: Running Review Analyzer on Sample ---")


# Prepare reviews and ids for analyze_reviews
sample_reviews = data["reviews"][:100]
sample_ids = data["ids"][:100]

analysis = analyze_reviews(sample_reviews, sample_ids)

print("LLM Analysis Output:\n")
for a in analysis:
    print(a)


#Aggregate results

agg = aggregate_results(analysis,
    data["reviews"])

print("\nAGGREGATION RESULT:")
print(agg["overall_ai_rating"])
print(agg["weighted_rating"])
print(agg["rating_stats"])
print(agg["sentiment_stats"])


#Outlier

outliers = detect_outliers(agg["ratings_dataframe"])

print("\nOUTLIER COUNTS:")
print(outliers["counts"])

print("\nStatistical Outliers:")
for r in outliers["statistical_outliers"]:
    print(r)

print("\nStrong Negative Reviews:")
for r in outliers["strong_negative_reviews"]:
    print(r)

print("\nStrong Positive Reviews:")
for r in outliers["strong_positive_reviews"]:
    print(r)

impact_results = analyze_impact(agg["ratings_dataframe"])

print("\nTOP 5 MOST INFLUENTIAL REVIEWS:")
for r in impact_results["most_influential_reviews"][:5]:
    print(r)