import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = "allam-2-7b"
TEMPERATURE = 0

CSV_COLUMNS = {
    "id": "ID",
    "name": "Name",
    "review": "Review",
    "rating": "Rating"
}
