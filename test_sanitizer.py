from ai.sanitizer import sanitize_email


email = """
CORRECTED EMAIL:

Dear Rahul Sharma,

This is a reminder that your payment of ₹400,000 is due on August 30, 2026.

Please make the payment at your convenience.

Best regards,

After-Sales Team
ABC Electronics

THE CORRECTIONS MADE ARE:

* Removed prohibited phrases.
* Kept the invoice number.
* Kept the amount.
"""


clean = sanitize_email(email)

print("SANITIZED EMAIL")
print("=" * 50)
print(clean)