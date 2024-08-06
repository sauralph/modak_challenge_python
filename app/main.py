from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from application.services import NotificationServiceApp
from domain.exceptions import RateLimitExceededException
from app.dependencies import get_notification_service_app
from infrastructure.auth import authenticate_admin_user, create_access_token, get_current_active_user, Token, ACCESS_TOKEN_EXPIRE_MINUTES

class NotificationRequest(BaseModel):
    notification_type: str
    recipient: str
    message: str

app = FastAPI()

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_admin_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/send-notification/")
def send_notification(
    request: NotificationRequest, 
    service: NotificationServiceApp = Depends(get_notification_service_app), 
    current_user: dict = Depends(get_current_active_user)
):
    try:
        service.send_notification(request.notification_type, request.recipient, request.message)
        return {"status": "success", "message": f"Notification sent to {request.recipient}"}
    except RateLimitExceededException as e:
        raise HTTPException(status_code=429, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
