import os

# Generate a secure random key (24 bytes)
jwt_secret_key = os.urandom(24).hex()

print("Generated JWT Secret Key:")
print(jwt_secret_key)
