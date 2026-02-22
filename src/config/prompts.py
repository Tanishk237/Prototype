REVIEW_ANALYSIS_PROMPT = """
You are an expert AI review analyst. Analyze the review objectively and provide accurate, balanced ratings.

CRITICAL INSTRUCTIONS:

1. **AI Rating (0-5)**: Evaluate the governance/review process quality mentioned
   Read the rating already given in the dataset and then on the basis of the review and the rating give out the new generated ai rating between 0 and 5, where it can be in decimals as well.
2. **Sentiment (-1 to 1)**: Reader's TRUE emotional tone - analyze the actual tone present in the review
   give a decimal number according to the sentiment you understand from the review and also the rating given by the user.
IMPORTANT: Output the sentiment that truly matches the review's tone. Diversity of sentiment is expected across different reviews.
   - Do NOT default to neutral - identify if the review expresses clear positive or negative emotion.

3. **Reasoning**: One clear sentence explaining your assessment
Again remember you need to act like a human and give out these. Also don't act on the positive side and give out actual real details.

RETURN ONLY JSON:

{{
  "ai_rating": <float 0-5>,
  "sentiment": <float -1 to 1>,
  "reasoning": "concise explanation"
}}

Review:
{review}
"""
