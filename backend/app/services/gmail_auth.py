import json
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from app.config import get_settings
from fastapi import HTTPException, status

settings = get_settings()

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/userinfo.email"
]


class GmailAuthService:
    @staticmethod
    def _get_cipher() -> Optional[Fernet]:
        key = settings.OAUTH_ENCRYPTION_KEY
        if not key:
            return None
        return Fernet(key.encode("utf-8"))

    @classmethod
    def _credentials_path(cls) -> Path:
        cred_dir = Path(settings.CREDENTIALS_DIR)
        cred_dir.mkdir(parents=True, exist_ok=True)
        return cred_dir / "gmail_token.enc"

    @classmethod
    def get_authorization_url(cls) -> str:
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google OAuth credentials are not configured in backend/.env"
            )

        client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        }

        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )
        return auth_url

    @classmethod
    def handle_oauth_callback(cls, code: str) -> str:
        client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        }

        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        flow.fetch_token(code=code)
        credentials = flow.credentials

        token_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }

        # Encrypt token payload at rest
        cipher = cls._get_cipher()
        serialized = json.dumps(token_data).encode("utf-8")
        encrypted = cipher.encrypt(serialized) if cipher else serialized

        with open(cls._credentials_path(), "wb") as f:
            f.write(encrypted)

        return "Gmail connected successfully."

    @classmethod
    def load_credentials(cls) -> Optional[Credentials]:
        cred_path = cls._credentials_path()
        if not cred_path.exists():
            return None

        try:
            with open(cred_path, "rb") as f:
                data = f.read()

            cipher = cls._get_cipher()
            decrypted = cipher.decrypt(data) if cipher else data
            token_dict = json.loads(decrypted.decode("utf-8"))

            creds = Credentials(
                token=token_dict.get("token"),
                refresh_token=token_dict.get("refresh_token"),
                token_uri=token_dict.get("token_uri"),
                client_id=token_dict.get("client_id"),
                client_secret=token_dict.get("client_secret"),
                scopes=token_dict.get("scopes")
            )

            # Refresh token if expired
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                cls.save_refreshed_credentials(creds)

            return creds
        except Exception:
            return None

    @classmethod
    def save_refreshed_credentials(cls, creds: Credentials):
        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes
        }
        cipher = cls._get_cipher()
        serialized = json.dumps(token_data).encode("utf-8")
        encrypted = cipher.encrypt(serialized) if cipher else serialized
        with open(cls._credentials_path(), "wb") as f:
            f.write(encrypted)

    @classmethod
    def is_connected(cls) -> bool:
        creds = cls.load_credentials()
        return creds is not None and creds.valid