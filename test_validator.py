from ai.validator import validate_email

email = """
Dear Rahul Sharma,

This is a polite reminder regarding the outstanding amount
of ₹400,000 against Invoice INV001, which is due on August 30, 2026.

We kindly request you to arrange the payment by the due date.

Thank you for your cooperation.

Best regards,
After-Sales Team
ABC Electronics
"""

result = validate_email(
    email,
    "Rahul Sharma",
    400000,
    "2026-08-30",
    "INV001",
    "Upcoming"
)

print("\nVALIDATION RESULT")
print("=" * 50)

print("Approved :", result["approved"])
print("Errors   :", result["errors"])
print("Sentiment:", result["sentiment"])