import jwt
import datetime

# Secret key used for JWT signing and verification (should be kept secret)
SECRET_KEY = 'secret_key'

# Example user data with passwords
users = {
    'user1': {'password': 'password1', 'user_id': 123, 'username': 'user1', 'email': 'user1@example.com'},
    'user2': {'password': 'password2', 'user_id': 456, 'username': 'user2', 'email': 'user2@example.com'}
}

# Function to generate JWT token after password authentication
def generate_token(username, password):
    user = users.get(username)
    if user and user['password'] == password:
        payload = {
            'user_id': user['user_id'],
            'username': user['username'],
            'email': user['email'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)  # Token expiration time
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return token
    else:
        return None

# Function to verify JWT token
def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Token is invalid
        return None

# Simple REST function requiring both token and password authentication
def pull_me_auth(token, username, password):
    decoded_token = verify_token(token)
    if decoded_token:
        user = users.get(decoded_token['username'])
        if user and user['password'] == password and user['username'] == username:
            return f"Authenticated user: {username}"
        else:
            return "Invalid username or password"
    else:
        return "Invalid or expired token"

# Example usage
# Generate token for user1
jwt_token_user1 = generate_token('user1', 'password1')
print("Generated JWT Token for user1:", jwt_token_user1)

# Verify token for user1
decoded_token_user1 = verify_token(jwt_token_user1)
if decoded_token_user1:
    print("Decoded Token for user1:", decoded_token_user1)
else:
    print("Invalid or expired token")

# Call pull_me_auth function with token authentication and password authentication
result = pull_me_auth(jwt_token_user1, 'user1', 'password1')
print("pull_me_auth result:", result)

