from transformers import pipeline

sentiment_model = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)

def analyze_sentiment(text):
    result = sentiment_model(text)[0]

    return {
        "label": result["label"],
        "score": round(result["score"], 3)
    }