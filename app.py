import pandas as pd
import time
from datetime import date
from ai.generator import generate_email, generate_response, regenerate_email
from ai.validator import validate_email
from ai.sanitizer import sanitize_email
from mailer.inbox import is_promotional, mark_read, message_details, read_unread_messages
from mailer.sender import send_email


REPLY_GENERATION_TIMEOUT = 20
REPLY_TOTAL_TIMEOUT = 10


# -----------------------------
# REMINDER SETTINGS
# -----------------------------

# AI sends reminders on these days before the due date
REMINDER_DAYS = [7, 3, 1, 0]


# -----------------------------
# LOAD DATA
# -----------------------------

customers = pd.read_csv("data/customers.csv")
sales = pd.read_csv("data/sales.csv")
finance = pd.read_csv("data/finance.csv")

for reminder_day in REMINDER_DAYS:
    reminder_column = f"reminder_{reminder_day}"
    if reminder_column not in finance:
        finance[reminder_column] = 0
    finance[reminder_column] = pd.to_numeric(
        finance[reminder_column], errors="coerce"
    ).fillna(0).astype(int)
if "reminder_overdue" not in finance:
    finance["reminder_overdue"] = 0
finance["reminder_overdue"] = pd.to_numeric(
    finance["reminder_overdue"], errors="coerce"
).fillna(0).astype(int)

finance["outstanding"] = (
    finance["invoice_amount"] - finance["amount_paid"]
)

finance["due_date"] = pd.to_datetime(
    finance["due_date"]
).dt.date


# -----------------------------
# MERGE DATA
# -----------------------------

data = finance.merge(
    customers,
    on="customer_id"
)

data = data.merge(
    sales,
    on=["customer_id", "order_id"]
)


# -----------------------------
# DUE DATE ENGINE
# -----------------------------

today = date.today()

data["days_left"] = data["due_date"].apply(
    lambda x: (x - today).days
)


def get_status(row):

    if row["outstanding"] <= 0:
        return "Paid"

    elif row["days_left"] < 0:
        return "Overdue"

    elif row["days_left"] == 0:
        return "Due Today"

    elif row["days_left"] <= 3:
        return "Due Soon"

    else:
        return "Upcoming"


data["reminder_status"] = data.apply(
    get_status,
    axis=1
)


# -----------------------------
# AUTOMATIC REMINDER CHECK
# -----------------------------

def should_send_reminder(row):

    # Already paid
    if row["outstanding"] <= 0:
        return False

    # Send each scheduled reminder only once, based on persisted finance data.
    days_left = row["days_left"]
    if days_left in REMINDER_DAYS:
        return int(row[f"reminder_{days_left}"]) == 0
    if days_left < 0:
        return int(row["reminder_overdue"]) == 0

    return False


def mark_reminder_sent(invoice_id, days_left):

    if days_left in REMINDER_DAYS:
        reminder_column = f"reminder_{days_left}"
    elif days_left < 0:
        reminder_column = "reminder_overdue"
    else:
        return

    matching_rows = finance[finance["invoice_id"] == invoice_id].index

    if matching_rows.empty:
        raise ValueError(f"Invoice not found: {invoice_id}")

    finance.loc[matching_rows, reminder_column] = 1
    finance.to_csv("data/finance.csv", index=False)


# -----------------------------
# PROCESS CUSTOMERS
# -----------------------------

pending = data[data["outstanding"] > 0]


for _, row in pending.iterrows():

    # Check whether today's date
    # requires a reminder

    if not should_send_reminder(row):

        print(
            f"⏭️ SKIPPED: {row['customer_name']} "
            f"| Due: {row['due_date']} "
            f"| Days left: {row['days_left']}"
        )

        continue


    print("\n")
    print("=" * 60)
    print("CUSTOMER:", row["customer_name"])
    print("STATUS:", row["reminder_status"])
    print("DAYS LEFT:", row["days_left"])
    print("=" * 60)


    # -----------------------------
    # GENERATE EMAIL
    # -----------------------------

    email = generate_email(
        row["customer_name"],
        row["company_name"],
        row["outstanding"],
        row["due_date"],
        row["invoice_id"],
        row["reminder_status"]
    )

    email = sanitize_email(email)


    print("\nGENERATED EMAIL")
    print("-" * 60)
    print(email)


    # -----------------------------
    # FIRST VALIDATION
    # -----------------------------

    result = validate_email(
        email,
        row["customer_name"],
        row["outstanding"],
        str(row["due_date"]),
        row["invoice_id"],
        row["reminder_status"]
    )


    print("\nVALIDATION")
    print("-" * 60)
    print("Approved :", result["approved"])
    print("Sentiment:", result["sentiment"])
    print("Errors   :", result["errors"])


    # -----------------------------
    # REGENERATE IF REJECTED
    # -----------------------------

    if not result["approved"]:

        print("\n❌ EMAIL REJECTED")
        print("Regenerating...")


        email = regenerate_email(
            email,
            result["errors"],
            row["customer_name"],
            row["company_name"],
            row["outstanding"],
            row["due_date"],
            row["invoice_id"],
            row["reminder_status"]
        )

        # Sanitize regenerated email
        email = sanitize_email(email)


        print("\nCORRECTED EMAIL")
        print("-" * 60)
        print(email)


        # -----------------------------
        # SECOND VALIDATION
        # -----------------------------

        result = validate_email(
            email,
            row["customer_name"],
            row["outstanding"],
            str(row["due_date"]),
            row["invoice_id"],
            row["reminder_status"]
        )


        print("\nSECOND VALIDATION")
        print("-" * 60)
        print("Approved :", result["approved"])
        print("Sentiment:", result["sentiment"])
        print("Errors   :", result["errors"])


    # -----------------------------
    # SEND EMAIL
    # -----------------------------

    if result["approved"]:

        print("\n✅ EMAIL APPROVED")
        print("Sending email...")


        subject = f"Payment Reminder - {row['invoice_id']}"


        send_email(
            row["email"],
            subject,
            email
        )

        mark_reminder_sent(row["invoice_id"], row["days_left"])


        print("✅ EMAIL SENT")
        print("To      :", row["email"])
        print("Subject :", subject)


    else:

        print("\n❌ EMAIL BLOCKED")
        print("Email will NOT be sent.")


def process_unread_mail():

    for uid, message in read_unread_messages():

        if is_promotional(message):
            print(f"SKIPPED PROMOTIONAL MAIL: {message.get('Subject', '')}")
            mark_read(uid)
            continue

        details = message_details(message)
        if not details["sender_email"]:
            mark_read(uid)
            continue

        try:
            started_at = time.monotonic()
            response = sanitize_email(
                generate_response(
                    details["sender_name"],
                    details["subject"],
                    details["body"],
                    timeout=REPLY_GENERATION_TIMEOUT
                )
            )
            remaining_time = REPLY_TOTAL_TIMEOUT - (time.monotonic() - started_at)
            if remaining_time <= 0:
                raise TimeoutError("Reply exceeded the 40-second total deadline")

            subject = details["subject"]
            if not subject.lower().startswith("re:"):
                subject = f"Re: {subject}"

            send_email(
                details["sender_email"],
                subject,
                response,
                in_reply_to=details["message_id"],
                references=details["references"],
                timeout=remaining_time
            )
            mark_read(uid)
            print(f"REPLIED TO: {details['sender_email']}")
        except Exception as error:
            print(f"MAIL FAILED; WILL RETRY: {error}")


if __name__ == "__main__":
    while True:
        try:
            process_unread_mail()
        except Exception as error:
            print(f"INBOX CHECK FAILED; WILL RETRY: {error}")
        time.sleep(120)