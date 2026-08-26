from ai.generator import generate_email

email = generate_email(
    "Rahul Sharma",
    "ABC Electronics",
    400000,
    "2026-08-30",
    "INV001",
    "Upcoming"
)

print("\nGENERATED EMAIL")
print("=" * 50)
print(email)