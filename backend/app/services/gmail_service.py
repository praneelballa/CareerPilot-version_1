import base64
import mimetypes
from email.message import EmailMessage
from pathlib import Path
from typing import Optional
from googleapiclient.discovery import build
from app.services.gmail_auth import GmailAuthService
from fastapi import HTTPException, status


class GmailService:
    @classmethod
    def get_user_email(cls) -> Optional[str]:
        creds = GmailAuthService.load_credentials()
        if not creds:
            return None
        try:
            service = build("gmail", "v1", credentials=creds)
            profile = service.users().getProfile(userId="me").execute()
            return profile.get("emailAddress")
        except Exception:
            return None

    @classmethod
    def send_application_email(
        cls,
        recipient: str,
        subject: str,
        body: str,
        attachment_path: Optional[str]
    ) -> str:
        creds = GmailAuthService.load_credentials()
        if not creds:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Gmail is not authorized. Please connect your Gmail account via OAuth first."
            )

        # 1. Build MIME multipart message (RFC 2822 compliant)
        msg = EmailMessage()
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content(body)

        # 2. Attach validated resume if present
        if attachment_path:
            att_path = Path(attachment_path)
            if not att_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Resume attachment not found at {attachment_path}"
                )

            mime_type, _ = mimetypes.guess_type(str(att_path))
            if not mime_type:
                mime_type = "application/octet-stream"
            maintype, subtype = mime_type.split("/", 1)

            with open(att_path, "rb") as f:
                file_data = f.read()

            msg.add_attachment(
                file_data,
                maintype=maintype,
                subtype=subtype,
                filename=att_path.name
            )

        # 3. Encode message as URL-safe base64 string
        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

        # 4. Dispatch using Gmail API
        try:
            service = build("gmail", "v1", credentials=creds)
            sent_msg = service.users().messages().send(
                userId="me",
                body={"raw": raw_message}
            ).execute()
            return sent_msg.get("id")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Gmail API transmission failed: {str(e)}"
            )