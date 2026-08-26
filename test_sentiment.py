from ai.sentiment import analyze_sentiment

email = """
Dear Rahul Sharma,

This is a polite reminder regarding the outstanding amount
of ₹400,000, which is due on August 30, 2026.

We appreciate your continued association with us and kindly
request you to arrange the payment by the due date.

Thank you for your cooperation.
"""

result = analyze_sentiment(email)

print("\nSENTIMENT ANALYSIS")
print("=" * 40)
print("Label :", result["label"])
print("Score :", result["score"])