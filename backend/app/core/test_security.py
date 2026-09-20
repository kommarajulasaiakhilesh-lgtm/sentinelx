from app.core.security import (
    hash_password,
    verify_password
)


password = "SentinelX@123"


hashed = hash_password(password)


print("Original password:")
print(password)

print()

print("Hashed password:")
print(hashed)

print()

print("Correct password:")
print(
    verify_password(
        password,
        hashed
    )
)

print()

print("Wrong password:")
print(
    verify_password(
        "WrongPassword",
        hashed
    )
)