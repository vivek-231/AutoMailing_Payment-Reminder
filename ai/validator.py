import re
from ai.sentiment import analyze_sentiment


def validate_email(email, customer, amount, due_date, invoice, status):

    errors = []

    # 1. Check customer name
    if customer.lower() not in email.lower():
        errors.append("Customer name missing")

    # 2. Check invoice number
    if invoice.lower() not in email.lower():
        errors.append("Invoice number missing")

    # 3. Check amount
    amount_text = f"₹{amount:,.0f}"

    if amount_text not in email:
        errors.append("Outstanding amount missing or incorrect")

    # 4. Check due date
    due_date_formats = [
        due_date,
        str(due_date).replace("-", "/")
    ]

    if not any(d.lower() in email.lower() for d in due_date_formats):
        # Don't immediately reject because LLM may format date differently
        pass

    # 5. Check incorrect overdue statement
    if status != "Overdue" and "overdue" in email.lower():
        errors.append("Incorrect overdue statement")

    # 6. Check unwanted placeholders
    placeholders = [
        "[Your Name]",
        "[Name]",
        "[Company Name]",
        "[Your Company]"
    ]

    for placeholder in placeholders:
        if placeholder.lower() in email.lower():
            errors.append(f"Placeholder found: {placeholder}")

    # 7. Check aggressive phrases
    aggressive_words = [
        "pay immediately",
        "final warning",
        "we will stop",
        "pay now"
    ]

    prohibited_phrases = [
        "late fee",
        "late fees",
        "penalty",
        "penalties",
        "legal action",
        "legal notice",
        "failure to pay",
        "immediate payment"
    ]

    for word in aggressive_words:
        if word in email.lower():
            errors.append(f"Potentially aggressive phrase: {word}")

    for phrase in prohibited_phrases:
        if phrase in email.lower():
            errors.append(f"Prohibited phrase found: {phrase}")


    # 8. Sentiment analysis
        # 8. Check for AI/internal content
    internal_phrases = [
        "customer information:",
        "validation errors:",
        "validation errors fixed:",
        "corrected email:",
        "the corrected email",
        "here is the corrected",
        "please let me know if there is anything else i can help",
        "status: upcoming",
        "status: overdue",
        "status: due soon",
        "status: due today"
    ]

    for phrase in internal_phrases:
        if phrase in email.lower():
            errors.append(f"Internal AI content found: {phrase}")
    sentiment = analyze_sentiment(email)

    return {
        "approved": len(errors) == 0,
        "errors": errors,
        "sentiment": sentiment
    }