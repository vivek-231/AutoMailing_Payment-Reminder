import requests


def generate_email(customer, company, amount, due_date, invoice, status):

    prompt = f"""
You are an AI assistant for a professional company's after-sales team.

Generate a short, professional and polite payment reminder email.

CUSTOMER INFORMATION:
Customer: {customer}
Company: {company}
Outstanding Amount: ₹{amount:,.0f}
Due Date: {due_date}
Invoice Number: {invoice}
Status: {status}

STATUS MEANING:
- Upcoming = payment is not due yet and is more than 2 days away.
- Due Soon = payment is due within 2 days.
- Due Today = payment is due today.
- Overdue = payment due date has already passed.

IMPORTANT RULES:
1. Never say the payment is overdue unless Status is Overdue.
2. Never mention late fees or penalties unless explicitly provided.
3. Never invent company policies.
4. Never change the amount, invoice number or due date.
5. Be professional, polite and respectful.
6. Use a warm but business-appropriate tone.
7. Do not use threatening or aggressive language.
8. Do not exaggerate the situation.
9. Clearly mention the outstanding amount and due date.
10. Keep the email concise.
11. Do not include placeholders such as [Your Name].
12. Return only the email body.

Create the reminder now.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama2",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]


def regenerate_email(
    old_email,
    errors,
    customer,
    company,
    amount,
    due_date,
    invoice,
    status
):

    prompt = f"""
You are correcting an automatically generated payment reminder.

CUSTOMER INFORMATION:
Customer: {customer}
Company: {company}
Outstanding Amount: ₹{amount:,.0f}
Due Date: {due_date}
Invoice Number: {invoice}
Status: {status}

PREVIOUS EMAIL:
{old_email}

VALIDATION ERRORS:
{errors}

Create a corrected version.

RULES:
- Fix every validation error.
- Never change the customer name.
- Never change the outstanding amount.
- Never change the invoice number.
- Never change the due date.
- Never say overdue unless the status is Overdue.
- Do not mention penalties or late fees unless explicitly provided.
- Do not use placeholders.
- Be professional and polite.
- Keep it concise.
- Return only the corrected email.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama2",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]


def generate_response(sender_name, subject, body, timeout=30):

    prompt = f"""
You are an AI assistant replying to an incoming business email.

SENDER: {sender_name}
SUBJECT: {subject}
MESSAGE:
{body}

Write a concise, professional and helpful reply.
Do not invent facts, commitments, prices, policies, or dates.
If the message needs information that is not provided, say that a team member
will review it. Do not mention that you are an AI. Return only the email body.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama2",
            "prompt": prompt,
            "stream": False
        },
        timeout=timeout
    )

    return response.json()["response"]