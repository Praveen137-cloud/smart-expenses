"""Train and save the expense-category classifier.

Run manually with:  python backend\train_classifier.py
This file is self-contained so it works both as a script and as an importable module.
"""
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

MODEL_PATH = Path(__file__).resolve().parent / "model" / "expense_classifier.pkl"

# Generic words that carry no category information.
STOP_WORDS = ["purchase", "payment", "to", "at", "the", "for", "of", "and", "with", "a", "in", "on"]

TRAINING_DATA = {
    "Food": [
        "starbucks coffee", "starbucks latte", "mcdonalds burger", "mcdonalds lunch", "swiggy food order",
        "zomato restaurant", "zomato dinner", "dominos pizza", "kfc chicken", "cafe coffee day",
        "walmart groceries", "grocery store vegetables", "big bazaar groceries", "biryani restaurant",
        "tea and snacks", "bakery cake", "lunch at canteen", "breakfast at hotel", "fruits and milk",
        "dinner with friends",
    ],
    "Transit": [
        "uber ride", "uber ride to college", "uber ride to office", "ola cab", "ola ride airport",
        "metro ticket", "metro card recharge", "bus ticket", "auto rickshaw fare", "petrol pump fuel",
        "diesel fuel", "train ticket irctc", "rapido bike taxi", "parking fee", "toll plaza", "flight ticket",
    ],
    "Utilities": [
        "electricity bill", "water bill", "internet bill", "broadband bill", "gas cylinder",
        "mobile recharge", "postpaid mobile bill", "wifi bill", "piped gas bill", "dth recharge",
        "municipal tax", "sewage charges",
    ],
    "Shopping": [
        "amazon order", "amazon purchase", "amazon headphones", "amazon shopping", "walmart shopping",
        "flipkart order", "flipkart headphones", "clothes purchase", "shoes purchase", "myntra clothing",
        "mobile phone accessories", "electronics store", "furniture purchase", "watch purchase",
        "ikea home decor", "laptop bag",
    ],
    "Entertainment": [
        "movie ticket", "cinema", "pvr cinemas", "inox movie", "concert ticket", "gaming credits",
        "steam game purchase", "bowling night", "amusement park", "theatre show", "playstation game",
        "club entry",
    ],
    "Healthcare": [
        "apollo pharmacy", "pharmacy medicine", "medical store", "doctor consultation", "hospital bill",
        "dental checkup", "eye checkup", "lab test", "health checkup", "medicines purchase",
        "physiotherapy session", "vitamin supplements",
    ],
    "Education": [
        "college books", "college fees", "udemy course", "coursera course", "exam fee", "tuition fees",
        "school stationery", "notebooks and pens", "online course", "library fine", "coaching classes",
        "textbooks purchase", "workshop registration",
    ],
    "Housing": [
        "house rent", "apartment rent", "rent payment", "monthly rent", "maintenance charges",
        "society maintenance", "home repair", "plumber charges", "security deposit", "pg rent",
        "hostel rent", "home loan emi",
    ],
    "Subscriptions": [
        "netflix subscription", "netflix monthly subscription", "spotify premium", "amazon prime membership",
        "youtube premium", "disney hotstar subscription", "icloud storage plan", "chatgpt plus subscription",
        "gym membership", "microsoft 365 subscription", "adobe subscription", "monthly subscription renewal",
    ],
    "Other": [
        "miscellaneous expense", "charity donation", "gift for friend", "bank charges", "cash withdrawal",
        "unknown expense", "courier charges", "laundry service", "haircut salon", "pet food",
    ],
}


def build_pipeline() -> Pipeline:
    return Pipeline([
        ("vectorizer", CountVectorizer(lowercase=True, ngram_range=(1, 2), stop_words=STOP_WORDS)),
        ("classifier", MultinomialNB(alpha=0.3)),
    ])


def train_and_save() -> Pipeline:
    """Train the pipeline on the built-in dataset, save it with joblib and return it."""
    texts, labels = [], []
    for category, examples in TRAINING_DATA.items():
        texts.extend(examples)
        labels.extend([category] * len(examples))
    pipeline = build_pipeline()
    pipeline.fit(texts, labels)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    return pipeline


if __name__ == "__main__":
    model = train_and_save()
    print(f"Trained on {sum(len(v) for v in TRAINING_DATA.values())} examples, "
          f"{len(TRAINING_DATA)} categories.")
    print(f"Model saved to: {MODEL_PATH}")
    for sample in ["Starbucks coffee", "Uber ride", "Amazon headphones", "Netflix monthly subscription"]:
        print(f"  {sample!r} -> {model.predict([sample])[0]}")
