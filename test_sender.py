from mailer.sender import send_email

print("Starting email test...")

send_email(
    "vivekvardhangolla@gmail.com",
    "AutoMailing Test",
    """Dear Vivek,

This is a test email from the AutoMailing system.

The email sender is working successfully.

Best regards,
AutoMailing System"""
)

print("Test completed.")