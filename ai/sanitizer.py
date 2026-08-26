import re


def sanitize_email(email):

    # --------------------------------
    # Remove unwanted headings
    # --------------------------------

    email = re.sub(
        r"^\s*CORRECTED EMAIL:\s*",
        "",
        email,
        flags=re.IGNORECASE
    )


    email = re.sub(
        r"^\s*GENERATED EMAIL:\s*",
        "",
        email,
        flags=re.IGNORECASE
    )


    # --------------------------------
    # Remove placeholders
    # --------------------------------

    placeholders = [
        r"\[Your Name\]",
        r"\[Name\]",
        r"\[Your Company\]",
        r"\[Company Name\]",
        r"\[Your Title\]",
        r"\[Your Email\]",
        r"\[Your Phone\]"
    ]

    for pattern in placeholders:

        email = re.sub(
            pattern,
            "",
            email,
            flags=re.IGNORECASE
        )


    # --------------------------------
    # Remove AI explanation sections
    # --------------------------------

    explanation_markers = [
        "VALIDATION ERRORS FIXED:",
        "THE CORRECTIONS MADE ARE:",
        "CORRECTIONS MADE:",
        "VALIDATION RESULT:",
        "VALIDATION EXPLANATION:"
    ]

    for marker in explanation_markers:

        match = re.search(
            re.escape(marker),
            email,
            flags=re.IGNORECASE
        )

        if match:
            email = email[:match.start()]


    # --------------------------------
    # Remove excessive blank lines
    # --------------------------------

    email = re.sub(
        r"\n\s*\n\s*\n+",
        "\n\n",
        email
    )


    # --------------------------------
    # Remove trailing whitespace
    # --------------------------------

    email = email.strip()


    return email