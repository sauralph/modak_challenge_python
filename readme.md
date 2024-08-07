# Challenge

## Quick Start
To run the application, you need to have Docker installed on your machine. You can run the application with the following command:

```sh
NO_AUTHORIZATION=1 docker-compose up -d
```

and access the frontend at `localhost:8000/static/index.html`

or perform a notification request with the following command:

```sh
curl -X POST "http://localhost:8000/send-notification/" -H "Content-Type: application/json" -d '{"notification_type": "status", "recipient": "user1@example.com", "message": "Status update 1"}'
```

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
NO_AUTHORIZATION=1 docker-compose up
```

### Sending a notification

The service must be running to send a notification. The following command sends a notification to the service.

```sh
curl -X POST "http://localhost:8000/send-notification/" -H "Content-Type: application/json" -d '{"notification_type": "status", "recipient": "user1@example.com", "message": "Status update 1"}'
```

## Using authorization
To use the authorization, you need to set the environment variables `SECRET_KEY`, `ADMIN_USER`, and `ADMIN_PASSWORD`. The following command sends a notification to the service with authorization.

```sh
# Launch service with authorization
ADMIN_PASSWORD=xxx docker-compose up -d 
curl -X 'POST' \
  'http://localhost:8000/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password&username=admin&password=xxx&scope=&client_id=string&client_secret=string'

curl -X 'POST' \
  'http://localhost:8000/send-notification/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <the_token>' \
  -H 'Content-Type: application/json' \
  -d '{
  "notification_type": "status",
  "recipient": "user1@example.com",
  "message": "Status update 1"
}'
```


## Endpoints

Endpoint documentation can be found at `http://localhost:8000/docs` or `http://localhost:8000/redoc`

## Available Environment Variables
### Redis Configuration
- `REDIS_HOST`: The host of the Redis server. Default: `localhost`
- `REDIS_PORT`: The port of the Redis server. Default: `6379`
### Authorization
- `NO_AUTHORIZATION`: If set to anything other than `0`, the service will not require authorization. Default: `0`
- `SECRET_KEY`: The secret key for JWT token. Default: `your_secret_key`
- `ADMIN_USER`: The admin username. Default: `admin`
- `ADMIN_PASSWORD`: The admin password. Default: `password`
