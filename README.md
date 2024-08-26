# E-commerce Web Scraper with FastAPI

This project is an asynchronous web scraper built with FastAPI, designed to extract product information from the target website [https://dentalstall.com/shop/](https://dentalstall.com/shop/). It uses PostgreSQL for data storage, Redis for caching, and can be deployed using Docker.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)

## Features

- Asynchronous web scraping using aiohttp and BeautifulSoup
- FastAPI for high-performance API endpoints
- PostgreSQL database for persistent storage
- Redis caching for improved performance
- Docker support for easy deployment
- Proxy support for web scraping
- Automatic retries with exponential backoff
- Notification system for scraping status updates (Console, Email, and Twilio SMS)
- Image downloading and storage
- API key authentication

## Prerequisites

- Python 3.9+
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL
- Redis

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/saksham1991999/ecommerce-scraper.git
   cd ecommerce-scraper
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the root directory by copying the `.env.template` file:
   ```
   cp .env.template .env
   ```

2. Open the `.env` file and update the environment variables with your specific values:
   ```
   # API Configuration
   API_KEY=your_secret_api_key

   # Database Configuration
   DATABASE_URL=postgresql+asyncpg://user:password@postgres/scraper_db

   # Redis Configuration
   REDIS_URL=redis://redis:6379

   # Twilio Configuration
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_FROM_NUMBER=your_twilio_phone_number
   TWILIO_TO_NUMBER=recipient_phone_number

   # Email Configuration
   EMAIL_SENDER=your_email@example.com
   EMAIL_PASSWORD=your_email_password
   EMAIL_RECEIVER=recipient_email@example.com

   # Other configurations...
   ```
   Make sure to replace the placeholder values with your actual configuration details.

   Note: A default API key is set in `docker-compose.yml` for quick setup. You can use this key to make requests without setting your own.

2. The `TARGET_URL` in `app/constants.py` is set to "https://dentalstall.com/shop/".

## Running the Application

### Local Development

1. Start the PostgreSQL and Redis services on your local machine.

2. Run the FastAPI application:
   ```
   uvicorn main:app --reload
   ```

3. The API will be available at `http://localhost:8000`.

### Docker Deployment

1. Build and start the Docker containers:
   ```
   docker-compose up --build
   ```

2. The API will be available at `http://localhost:8000`.

## API Endpoints

- `POST /api/v1/scrape`: Start a scraping job
  - Query Parameters:
    - `page_limit` (optional): Maximum number of pages to scrape
    - `proxy` (optional): Proxy URL to use for scraping

## Usage

To start a scraping job, send a POST request to the `/api/v1/scrape` endpoint:
```bash
curl -X POST "http://localhost:8000/api/v1/scrape?page_limit=5" \
-H "X-API-Key: 51Nj8UxKGLqm7Xt9Aw3RzBvF8qY6cJpL2tMn7DkZxC9Hs5EoVfGjTy2Lm1Rk3Pb8N"
```

## Project Structure

The project structure has been updated to include new components and services. Here's an overview of the main directories and files:

```
ecommerce-scraper-fastapi/
├── app/
│   ├── cache/
│   ├── exceptions/
│   ├── middleware/
│   ├── models/
│   ├── notifications/
│   ├── repositories/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── utils/
├── storage/
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── main.py
├── README.md
└── requirements.txt
```
