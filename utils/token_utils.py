import jwt
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple

def parse_id_token(token: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Parses a JWT token into its header and payload without verifying the signature.
    Useful for debugging and inspecting exactly what is inside the token.
    """
    try:
        header = jwt.get_unverified_header(token)
        payload = jwt.decode(token, options={"verify_signature": False}, algorithms=["HS256", "RS256", "ES256"])
        return header, payload
    except Exception as e:
        raise ValueError(f"Invalid JWT format: {e}")

def get_mock_oidc_token() -> str:
    """
    Generates a mock OIDC token for testing the UI without Okta connection.
    """
    header = {
        "alg": "HS256",
        "kid": "mock-key-id-12345"
    }
    
    now = datetime.now(timezone.utc)
    
    payload = {
        "sub": "mock_user_123",
        "name": "Jean Dupont",
        "email": "jean.dupont@mock.com",
        "preferred_username": "jdupont",
        "ver": 1,
        "iss": "https://dev-mock.oktapreview.com",
        "aud": "mock-client-id-abcde",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp()),
        "jti": "id.mock-jti-123",
        "amr": ["pwd", "mfa"],
        "idp": "00o00000000000000",
        "auth_time": int((now - timedelta(minutes=5)).timestamp()),
        "groups": ["Admins", "Users", "Developers"],
        "roles": ["read", "write"]
    }
    
    # Sign with a mock symmetric key for structural validity
    token = jwt.encode(payload, "mock_secret", algorithm="HS256")
    return token
