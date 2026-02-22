# CSV loader node
import pandas as pd
from pathlib import Path
from src.config.settings import CSV_COLUMNS


def load_csv(file_path):
    # Try the provided path first, then resolve relative to project root if not found
    path = Path(file_path)
    if not path.exists():
        # project root assumed two levels up from this file
        project_root = Path(__file__).resolve().parents[2]
        alt_path = project_root / file_path
        if alt_path.exists():
            path = alt_path

    df = pd.read_csv(path)

    ids = df[CSV_COLUMNS["id"]].tolist()
    reviews = df[CSV_COLUMNS["review"]].astype(str).tolist()

    return {
        "reviews": reviews,
        "ids": ids,
        "total_reviews": len(reviews)
    }
