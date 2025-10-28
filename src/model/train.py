import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Simple training data
data = [
    ("I love this product", "positive"),
    ("This is amazing", "positive"),
    ("Terrible experience", "negative"),
    ("Waste of money", "negative"),
    # Add 20-30 more examples
]

df = pd.DataFrame(data, columns=["text", "sentiment"])

# Create simple pipeline
model = Pipeline(
    [
        ("tfidf", TfidfVectorizer(max_features=1000)),
        ("classifier", LogisticRegression()),
    ]
)

model.fit(df["text"], df["sentiment"])
joblib.dump(model, "model.pkl")
print("✅ Model trained and saved!")
