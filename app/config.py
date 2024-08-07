from pydantic import BaseModel

class RateLimits(BaseModel):
    status_count: int = 2
    status_period: int = 60
    news_count: int = 1
    news_period: int = 86400
    marketing_count: int = 3
    marketing_period: int = 3600

rate_limits_config = RateLimits()
