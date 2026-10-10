from fastapi import APIRouter, Query, status
from fastapi.responses import RedirectResponse
from app.services.gmail_auth import GmailAuthService
from app.services.gmail_service import GmailService
from app.schemas.application import GmailAuthStatus

router = APIRouter()


@router.get("/status", response_model=GmailAuthStatus, status_code=status.HTTP_200_OK)
async def get_status():
    connected = GmailAuthService.is_connected()
    email_addr = GmailService.get_user_email() if connected else None
    return GmailAuthStatus(is_connected=connected, email_address=email_addr)


@router.get("/connect", status_code=status.HTTP_200_OK)
async def connect_gmail():
    url = GmailAuthService.get_authorization_url()
    return {"authorization_url": url}


@router.get("/callback", status_code=status.HTTP_200_OK)
async def oauth_callback(code: str = Query(...)):
    GmailAuthService.handle_oauth_callback(code)
    # Redirect back to frontend settings or review screen
    return RedirectResponse(url="http://localhost:5173/?gmail=connected")