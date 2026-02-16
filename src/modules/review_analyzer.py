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
        json_text = text[start:end + 1]
        return json.loads(json_text)

    return None


def analyze_reviews(reviews, ids):
    """
    Analyze reviews using LLM.
    Returns structured output with:
    - id
    - ai_rating (float, 1.0 to 5.0)
    - sentiment (float, -1.0 to 1.0)
    - reasoning
    """

    results = []

    for review_text, review_id in zip(reviews, ids):

        parsed = None

        try:
            # First attempt
            response = chain.invoke({"review": review_text})
            raw_output = getattr(response, "content", str(response))
            parsed = extract_json_from_text(raw_output)

        except Exception:
            parsed = None

        # Retry once if parsing failed
        if parsed is None:
            try:
                retry_prompt = (
                    "Return ONLY valid JSON with keys: "
                    "\"ai_rating\" (float 1.0-5.0), "
                    "\"sentiment\" (float -1.0 to 1.0), "
                    "\"reasoning\".\n\nReview:\n"
                    + review_text
                )
                retry_response = llm.invoke(retry_prompt)
                retry_raw = getattr(retry_response, "content", str(retry_response))
                parsed = extract_json_from_text(retry_raw)
            except Exception:
                parsed = None

        # If still failed → fallback
        if parsed is None:
            clean_output = {
                "id": review_id,
                "ai_rating": 3.0,
                "sentiment": 0.0,
                "reasoning": "Parsing error or invalid model response"
            }

        else:
            # Extract values
            try:
                ai_rating = float(parsed.get("ai_rating", 3.0))
            except Exception:
                ai_rating = 3.0

            try:
                sentiment = float(parsed.get("sentiment", 0.0))
            except Exception:
                sentiment = 0.0

            # Clamp to valid ranges
            ai_rating = max(1.0, min(5.0, ai_rating))
            sentiment = max(-1.0, min(1.0, sentiment))

            clean_output = {
                "id": review_id,
                "ai_rating": round(ai_rating, 2),     
                "sentiment": round(sentiment, 3),     
                "reasoning": str(parsed.get("reasoning", ""))
            }

        results.append(clean_output)

    return results
