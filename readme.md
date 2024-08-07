# Challenge

## Specification
We have a Notification system that sends out email notifications of various types (status update, daily news, project invitations, etc). We need to protect recipients from getting too many emails, either due to system errors or due to abuse, so let’s limit the number of emails sent to them by implementing a rate-limited version of NotificationService.
The system must reject requests that are over the limit.
Some sample notification types and rate limit rules, e.g.:

- Status: not more than 2 per minute for each recipient
- News: not more than 1 per day for each recipient
- Marketing: not more than 3 per hour for each recipient
Etc. these are just samples, the system might have several rate limit rules!

## Running the application
### Building the application with Docker

```sh
docker-compose build

```

### Running the application with Docker

```sh
docker-compose up
```

### Sending a notification

The service must be running to send a notification. The following command sends a notification to the service.

```sh
curl -X POST "http://localhost:8000/send-notification/" -H "Content-Type: application/json" -d '{"notification_type": "status", "recipient": "user1@example.com", "message": "Status update 1"}'
```

## Endpoints

Endpoint documentation can be found at `http://localhost:8000/docs` or `http://localhost:8000/redoc`

## Available Environment Variables
### Redis Configuration
- `REDIS_HOST`: The host of the Redis server. Default: `localhost`
- `REDIS_PORT`: The port of the Redis server. Default: `6379`
### Authorization
- `SECRET_KEY`: The secret key for JWT token. Default: `your_secret_key`
- `ADMIN_USER`: The admin username. Default: `admin`
- `ADMIN_PASSWORD`: The admin password. Default: `password`
### Rate Limiting
- `STATUS_COUNT`: Maximum number of status notifications that can be sent in a period. Default: `2` 
- `STATUS_PERIOD`: The period in seconds for the status notifications in seconds. Default: `60`
- `NEWS_COUNT`: Maximum number of news notifications that can be sent in a period. Default: `1`
- `NEWS_PERIOD`: Maximum number of news notifications that can be sent in a period in seconds. Default: `86400`
- `MARKETING_COUNT`: Maximum number of marketing notifications that can be sent in a period. Default: `3`
- `MARKETING_PERIOD`: Maximum number of marketing notifications that can be sent in a period in seconds. Default: `3600` 
