from pathlib import Path
import csv
import re

import joblib


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[3]

MODEL_DIR = BASE_DIR / "AI" / "model"

MODEL_PATH = MODEL_DIR / "PHARVO_svm_FINAL.pkl"
MAPPING_PATH = MODEL_DIR / "PHARVO_36class_mapping_FINAL.csv"


# --------------------------------------------------
# Load trained SVM model once
# --------------------------------------------------

_model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# Load 36-class medicine mapping
# --------------------------------------------------

_problem_mapping = {}

with open(
    MAPPING_PATH,
    "r",
    encoding="utf-8-sig",
    newline=""
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        generics = [
            item.strip()
            for item in row["candidate_generics"].split(";")
            if item.strip()
        ]

        _problem_mapping[row["problem_id"]] = {
            "health_problem": row["health_problem"],
            "candidate_generics": generics,
        }


# --------------------------------------------------
# Bangla / Banglish query normalization
# --------------------------------------------------

def normalize_query(text: str) -> str:

    original = str(text).strip()
    normalized = original.casefold()

    gastric_patterns = [
        r"গ্যাসের সমস্যা",
        r"গ্যাস সমস্যা",
        r"অ্যাসিডিটি",
        r"এসিডিটি",
        r"\bgas er somossa\b",
        r"\bgas er problem\b",
        r"\bgastric problem\b",
    ]

    for pattern in gastric_patterns:

        if re.search(pattern, normalized):
            return original + " gastric acidity problem"

    return original


# --------------------------------------------------
# Predict health problem
# --------------------------------------------------

def predict_health_problem(text: str) -> dict:

    if not text or not str(text).strip():
        raise ValueError("Query text cannot be empty.")

    normalized_text = normalize_query(text)

    problem_id = _model.predict(
        [normalized_text]
    )[0]

    info = _problem_mapping.get(
        problem_id,
        {}
    )

    return {
        "input_text": text,
        "normalized_query": normalized_text,
        "problem_id": problem_id,
        "health_problem": info.get("health_problem"),
        "candidate_generics": info.get(
            "candidate_generics",
            []
        ),
        "confidence": None,
        "requires_pharmacist_review": True,
    }