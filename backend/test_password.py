from services.password_service import hash_password, verify_password

password = "MarketIQ123"

# Hash the password
hashed = hash_password(password)

print("Original Password :", password)
print("Hashed Password   :", hashed)

# Verify correct password
print("Correct Password :", verify_password(password, hashed))

# Verify wrong password
print("Wrong Password   :", verify_password("WrongPassword", hashed))