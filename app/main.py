from typing import Optional
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from application.services import NotificationServiceApp
from domain.exceptions import RateLimitExceededException
from app.dependencies import get_notification_service_app
from app.config import rate_limits_config
from fastapi.staticfiles import StaticFiles
from infrastructure.auth import authenticate_admin_user, create_access_token, get_current_active_user, Token, ACCESS_TOKEN_EXPIRE_MINUTES

class NotificationRequest(BaseModel):
    notification_type: str = Field(..., json_schema_extra={"example": "status"})
    recipient: str = Field(..., json_schema_extra={"example": "user1@example.com"})
    message: str = Field(..., json_schema_extra={"example": "Status update 1"})

class NotificationResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "success"})
    message: str = Field(..., json_schema_extra={"example": "Notification sent to user1@example.com"})

class ErrorResponse(BaseModel):
    detail: str = Field(..., json_schema_extra={"example": "Rate limit exceeded for status to user1@example.com"})

class RateLimitUpdateRequest(BaseModel):
    status_count: Optional[int] = Field(None, json_schema_extra={"example": 2})
    status_period: Optional[int] = Field(None, json_schema_extra={"example": 60})
    news_count: Optional[int] = Field(None, json_schema_extra={"example": 1})
    news_period: Optional[int] = Field(None, json_schema_extra={"example": 86400})
    marketing_count: Optional[int] = Field(None, json_schema_extra={"example": 3})
    marketing_period: Optional[int] = Field(None, json_schema_extra={"example": 3600})

app = FastAPI(
    title="Notification API",
    description="API for sending notifications with rate limiting and JWT authentication",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/token", response_model=Token, summary="Login for access token", description="Login using the admin credentials to obtain a JWT access token.")
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

@app.post("/send-notification/",
          summary="Send a notification",
          description="Send a notification to a specified recipient. Requires JWT authentication.",
          responses={
              200: {"description": "Notification sent successfully", "model": NotificationResponse},
              400: {"description": "Invalid request", "model": ErrorResponse},
              429: {"description": "Rate limit exceeded", "model": ErrorResponse},
              401: {"description": "Unauthorized", "model": ErrorResponse}
          })
def send_notification(
    request: NotificationRequest = Body(..., json_schema_extra={"example":{
        "notification_type": "status",
        "recipient": "user1@example.com",
        "message": "Status update 1"
    }}),
    service: NotificationServiceApp = Depends(get_notification_service_app),
    current_user: dict = Depends(get_current_active_user)
):
    # External validation for the request
    recipient = request.recipient.strip()
    if not recipient or "@" not in recipient:
        raise HTTPException(status_code=400, detail="Invalid recipient email") 
    
    try:
        service.send_notification(request.notification_type, request.recipient, request.message)
        return {"status": "success", "message": f"Notification sent to {request.recipient}"}
    except RateLimitExceededException as e:
        raise HTTPException(status_code=429, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/rate-limits/", 
         summary="Update rate limits", 
         description="Update the rate limits for notifications. Requires JWT authentication.",
         responses={
             200: {"description": "Rate limits updated successfully", "model": NotificationResponse},
             400: {"description": "Invalid request", "model": ErrorResponse},
             401: {"description": "Unauthorized", "model": ErrorResponse}
         })
def update_rate_limits(
    rate_limit_update: RateLimitUpdateRequest,
    current_user: dict = Depends(get_current_active_user)
):
    if rate_limit_update.status_count is not None:
        rate_limits_config.status_count = rate_limit_update.status_count
    if rate_limit_update.status_period is not None:
        rate_limits_config.status_period = rate_limit_update.status_period
    if rate_limit_update.news_count is not None:
        rate_limits_config.news_count = rate_limit_update.news_count
    if rate_limit_update.news_period is not None:
        rate_limits_config.news_period = rate_limit_update.news_period
    if rate_limit_update.marketing_count is not None:
        rate_limits_config.marketing_count = rate_limit_update.marketing_count
    if rate_limit_update.marketing_period is not None:
        rate_limits_config.marketing_period = rate_limit_update.marketing_period
    return {"status": "success", "message": "Rate limits updated successfully"}

@app.delete("/notifications", 
            summary="Clear all notifications",
            description="Clear all notifications. Requires JWT authentication.",
            responses={
                200: {"description": "All notifications cleared successfully", "model": NotificationResponse},
                401: {"description": "Unauthorized", "model": ErrorResponse}
            })
def clear_all_notifications(service: NotificationServiceApp = Depends(get_notification_service_app), current_user: dict = Depends(get_current_active_user)):
    service.clear_all_notifications()
    return {"status": "success", "message": "All notifications cleared successfully"}

@app.get("/rate-limits/", summary="Get rate limits", description="Fetch the current rate limits.", responses={
    200: {"description": "Rate limits fetched successfully", "model": RateLimitUpdateRequest},
    401: {"description": "Unauthorized", "model": ErrorResponse}
})
def get_rate_limits(current_user: dict = Depends(get_current_active_user)):
    return {
        "status_count": rate_limits_config.status_count,
        "status_period": rate_limits_config.status_period,
        "news_count": rate_limits_config.news_count,
        "news_period": rate_limits_config.news_period,
        "marketing_count": rate_limits_config.marketing_count,
        "marketing_period": rate_limits_config.marketing_period
    }

@app.get("/usage/",
         summary="Get all users notification usage",
         description="Fetch the notification usage for all users. Requires JWT authentication.",
         responses={
             200: {"description": "All users usage fetched successfully"},
             401: {"description": "Unauthorized", "model": ErrorResponse}
         })
def get_all_users_usage(service: NotificationServiceApp = Depends(get_notification_service_app), current_user: dict = Depends(get_current_active_user)):
    usage = service.get_all_usage()
    return usage