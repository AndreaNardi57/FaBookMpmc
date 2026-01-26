from passlib.context import CryptContext

# 1. Create a CryptContext instance, specifying the encryption algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. Function to verify password
def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 3. Function to generate password hash
def get_password_hash(password) -> str:
    return pwd_context.hash(password)