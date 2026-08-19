from services.jwt_service import create_access_token, verify_access_token

token = create_access_token(
    {
        "sub": "bhupendra@gmail.com",
        "user_id": "12345",
    }
)

print("JWT Token:\n")
print(token)

print("\nDecoded:\n")

print(verify_access_token(token))