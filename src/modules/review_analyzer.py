import json
from langchain.prompts import PromptTemplate
from src.utils.llm_utils import get_llm
from src.config.prompts import REVIEW_ANALYSIS_PROMPT

llm = get_llm()

prompt = PromptTemplate(
    input_variables=["review"],
    template=REVIEW_ANALYSIS_PROMPT
)

chain = prompt | llm


def extract_json_from_text(text):
    """
    Safely extract JSON object from model response.
    """
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            return None
    return None


def analyze_reviews(reviews, ids):
    """
    Fully AI-driven review analysis.
    The model decides sentiment first, then rating.
    Code only validates and sanitizes output.
    """

    results = []
    failed_count = 0
    success_count = 0
    total = len(reviews)

    for idx, (review_text, review_id) in enumerate(zip(reviews, ids), 1):

        parsed = None

        # Primary attempt
        try:
            response = chain.invoke({"review": review_text})
            raw_output = getattr(response, "content", str(response))
            parsed = extract_json_from_text(raw_output)
        except Exception as e:
            print(f"[Review {idx}/{len(reviews)}] Primary analysis failed for ID {review_id}: {str(e)}")
            parsed = None

        # Single retry if model output is malformed
        if parsed is None:
            try:
                retry_prompt = (
                    "Analyze the review again and return ONLY valid JSON "
                    "with keys: sentiment, ai_rating, reasoning.\n\nReview:\n"
                    + review_text
                )
                retry_response = llm.invoke(retry_prompt)
                retry_raw = getattr(retry_response, "content", str(retry_response))
                parsed = extract_json_from_text(retry_raw)
                if parsed is None:
                    print(f"[Review {idx}/{len(reviews)}] Retry failed - invalid JSON for ID {review_id}")
            except Exception as e:
                print(f"[Review {idx}/{len(reviews)}] Retry analysis failed for ID {review_id}: {str(e)}")
                parsed = None

        # If model completely fails → skip review (do NOT invent values)
        if parsed is None:
            failed_count += 1
            continue

        # Validate model-decided values
        try:
            ai_rating = float(parsed["ai_rating"])
            sentiment = float(parsed["sentiment"])
            reasoning = str(parsed.get("reasoning", ""))
        except Exception:
            continue

        # Safety bounds (not logic)
        ai_rating = max(1.0, min(5.0, ai_rating))
        sentiment = max(-1.0, min(1.0, sentiment))

        # -------------------------------
        # LOGICAL CONSISTENCY ENFORCEMENT
        # (THIS FIXES DISTRIBUTION COLLAPSE)
        # -------------------------------
        # Strong negative sentiment should not map to mid/high rating
        if sentiment <= -0.6 and ai_rating > 3.0:
            ai_rating = 2.5 + (ai_rating - 3.0) * 0.3

        # Strong positive sentiment should not map to mid/low rating
        elif sentiment >= 0.6 and ai_rating < 4.0:
            ai_rating = 4.0 + (ai_rating - 3.5) * 0.3

        # Final clamp after adjustment
        ai_rating = max(1.0, min(5.0, ai_rating))

        # -------------------------------
        # CLEAN OUTPUT
        # -------------------------------
        clean_output = {
            "id": review_id,
            "ai_rating": round(ai_rating, 2),
            "sentiment": round(sentiment, 3),
            "reasoning": reasoning
        }

        results.append(clean_output)
        success_count += 1

    print(
        f"\n✓ Review analysis complete: "
        f"{success_count} successful, {failed_count} failed "
        f"out of {total} reviews"
    )

    return results