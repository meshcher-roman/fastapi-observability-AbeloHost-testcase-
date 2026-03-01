# FastAPI Observability Project 
This project demonstrates a production-ready FastAPI application with a complete Observability stack using Prometheus, Grafana, Loki, and Promtail.

## Tech Stack
- **Backend:** FastAPI, Python 3.11, SQLAlchemy (async), asyncpg
- **Database:** PostgreSQL 15
- **Observability:** Prometheus, Grafana, Loki, Promtail
- **Deployment:** Docker, Docker Compose
- **Testing:** Pytest, HTTPX

## How to Run

1. Clone the repository and navigate to the project directory.
2. Build and start the infrastructure using Docker Compose:
   ```bash
   docker-compose up -d --build
   ```
3. The database will be automatically seeded with mock data on startup.
## Services Overview

|**Service**|**Address / URL**|**Description**|
|---|---|---|
|**FastAPI App**|`http://localhost:8000`|Main application|
|**API Docs**|`http://localhost:8000/docs`|Swagger UI|
|**Metrics**|`http://localhost:8000/metrics`|Prometheus metrics endpoint|
|**Grafana**|`http://localhost:3000`|Dashboards (Login: `admin` / Password: `admin`)|
|**Prometheus**|`http://localhost:9090`|Metrics scraping and alerts|

## Observability Features
### 1. Secure JSON Logging

The application uses `python-json-logger` to format all logs in JSON format. Promtail securely reads these logs directly from the Docker container files (without exposing the Docker socket) and pushes them to Loki. You can view the logs in Grafana by querying: `{job="docker_containers"} | json`

### 2. Automated Metrics

The project uses `prometheus-fastapi-instrumentator` to automatically instrument the FastAPI application. It tracks standard HTTP metrics including:

- `http_requests_total` (Counter): Total number of requests by status code and handler.
- `http_request_duration_seconds` (Histogram): Request latency/duration.
### 3. Grafana Dashboard (Provisioning)
Dashboards and Data Sources are provisioned automatically (no manual import required!).

1. Open Grafana (`http://localhost:3000`).
2. Login with `admin` / `admin`.
3. Go to **Dashboards** -> **Default Dashboards** -> **FastAPI Observability Pro**. It includes pre-configured panels for RPS, 95th Percentile Latency, HTTP Errors, System CPU/RAM usage, and Application Logs.
### 4. Bottleneck Simulation & Alerts
The endpoint `POST /process` simulates a bottleneck using `await asyncio.sleep(0.5)`. A custom Prometheus alert (`HighRequestLatency`) is configured in `alerts.yml`. It fires a **Critical** alert if the 90th percentile of request latency exceeds 1 second. You can view the alert status at `http://localhost:9090/alerts`.

## Testing
The project includes integration and unit tests using `pytest` and mock database sessions to ensure isolated testing without relying on the actual PostgreSQL instance.

To run the tests locally:



``` Bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pytest -v
```