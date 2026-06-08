<div align="center">
  <h1>🔗 LinkForge — Scalable URL Shortener</h1>
  <p>A high-performance URL shortening service designed with real-world backend architecture principles, focusing on caching, asynchronous processing, and scalable request handling.</p>
  
  <p>
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
    <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
    <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis" />
    <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  </p>
</div>

<hr/>

## 📸 Project Screenshots

Here is a glimpse of the premium, dark-mode focused UI built from scratch using strict CSS variables, glassmorphism, and dynamic animations.

<div align="center">
    <img src="screenshot/Screenshot%202026-04-02%20181042.png" alt="Analytics View" width="800" style="border-radius:10px; margin-bottom:15px;" />
  <br/>
    <img src="screenshot/Screenshot%202026-04-02%20180734.png" alt="Dashboard View" width="800" style="border-radius:10px; margin-bottom:15px;" />
  <br/>
  <img src="screenshot/Screenshot%202026-04-02%20181101.png" alt="Create Link View" width="800" style="border-radius:10px;" />
</div>

<br/>

## 🌟 Features

- ⚡ **Blazing Fast Redirects**: Redis caching ensures minimal latency for URL resolution.
- 🔢 **Base62 Encoding**: Short, efficient, and collision-resistant URL codes.
- ✏️ **Custom Aliases**: Users can choose their own memorable custom short codes.
- 📊 **Advanced Analytics**: Track total clicks, unique visitors, click geographic locations, and time-based metrics.
- ⏳ **Link Expiration**: Set URLs to automatically expire after a specified duration.
- ⚙️ **Background Processing**: Click event aggregation and expired link cleanup handled asynchronously via Celery.
- 🛡️ **Rate Limiting**: Built-in API rate limiting to prevent abuse and ensure stability.
- 🔒 **JWT Authentication**: Secure user registration, login, and protected routes.
- 📱 **QR Code Generation**: Automatically generate downloadable QR codes for shortened URLs.

## 🏗️ Architecture Stack

- **Frontend**: React 18, Vite, Recharts (for analytics), Vanilla CSS (Design system with tokens).
- **Backend API**: FastAPI (Python), providing asynchronous endpoints and Pydantic validation.
- **Primary Database**: PostgreSQL 16 for persistent storage of users, URLs, and granular click logs.
- **Cache & Message Broker**: Redis 7 for high-speed URL resolution caching and Celery task queuing.
- **Background Workers**: Celery workers & beat scheduler for asynchronous processing (daily analytics aggregation, URL cleanup).
- **Deployment**: Fully containerized using Docker and Docker Compose.

---

## 🚀 Getting Started

### Prerequisites
- [Docker](https://www.docker.com/) and Docker Compose installed on your system.

### 1. Environment Setup

The repository comes with a `.env.example` file. Copy this to a `.env` file before starting the application:

```bash
cp .env.example .env
```
*(You may adjust the predefined secrets and configuration inside `.env` as needed).*

### 2. Start the Application

**🌟 For Windows Users (1-Click Setup):**
Simply double-click the `setup_and_run.bat` file in the project folder. 
It will automatically:
- Check if Docker is running
- Auto-generate the `.env` configuration file
- Install dependencies and build all Docker containers
- Start the server and provide the necessary URLs

**🍎 For Mac/Linux Users (Manual):**
Build and start all services using Docker Compose:

```bash
docker-compose up --build -d
```

This command will spin up the following containers:
- `shortener-db` (PostgreSQL)
- `shortener-redis` (Redis)
- `shortener-backend` (FastAPI at `http://localhost:8000`)
- `shortener-celery-worker` (Async task processor)
- `shortener-celery-beat` (Cron-like task scheduler)
- `shortener-frontend` (React App at `http://localhost:5173`)

## 🛠️ Data Flow & Background Tasks

1. **Shortening**: A user submits a URL via the UI. The FastAPI backend validates it, generates a Base62 hash (or uses a custom alias), saves it to PostgreSQL, and preemptively caches it in Redis.
2. **Redirection**: When a short URL is accessed, the backend checks Redis first (O(1) lookup). If a cache miss occurs, it hits PostgreSQL, caches the result, and redirects the user.
3. **Analytics**: The click event is immediately logged to the `clicks` table.
4. **Aggregation**: `celery-beat` triggers an hourly task that aggregates raw clicks into the `daily_analytics` table for highly efficient dashboard querying.
5. **Cleanup**: Expired URLs are safely deactivated and purged from the Redis cache by another recurring Celery task.

---
⚠️ Positioning (Honest)

This project is not deployed at production scale, but is architected using patterns commonly used in real-world systems:
-Cache-first data access
-Asynchronous background processing
-Separation of read/write workloads

## 🧪 Running Tests

LinkForge has a comprehensive test suite of 95 unit and integration tests covering encoding, validation, caching, security hardening, user registration/login, and URL lifecycle resolution.

### Running Backend Tests Locally

1. Make sure you are inside the virtual environment:
   ```bash
   cd backend
   # Windows
   .venv\Scripts\activate
   # Mac/Linux
   source .venv/bin/activate
   ```

2. Run the test suite:
   ```bash
   python -m pytest
   ```
   *Note: If PostgreSQL is not running locally, the test suite automatically falls back to an in-memory SQLite database (`sqlite+aiosqlite:///:memory:`).*

3. Run tests with coverage and generate reports:
   ```bash
   python -m pytest --cov=app --cov-report=term --cov-report=html
   ```
   *The HTML coverage report will be generated under the `htmlcov/` directory.*

---

## 🛑 Stopping the Application

**For Windows Users:**
Just double-click the `stop.bat` script to safely shut down all services.

**For Mac/Linux Users:**
To gracefully stop all services without losing database data:

```bash
docker-compose down
```

To stop services and completely wipe all volumes (database and cache data):

```bash
docker-compose down -v
```
