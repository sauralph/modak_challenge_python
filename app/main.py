from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from application.services import NotificationServiceApp
from domain.exceptions import RateLimitExceededException
from .dependencies import get_notification_service_app

class NotificationRequest(BaseModel):
    notification_type: str
    recipient: str
    message: str

app = FastAPI()

@app.post("/send-notification/")
def send_notification(request: NotificationRequest, service: NotificationServiceApp = Depends(get_notification_service_app)):
    try:
        service.send_notification(request.notification_type, request.recipient, request.message)
        return {"status": "success", "message": f"Notification sent to {request.recipient}"}
    except RateLimitExceededException as e:
        raise HTTPException(status_code=429, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
