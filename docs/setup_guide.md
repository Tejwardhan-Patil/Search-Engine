# Setup Guide

This document provides a step-by-step guide for setting up the search engine.

## Prerequisites

- Python 3.8 or higher
- Java JDK 11 or higher
- Go 1.16 or higher
- Docker (for containerization)
- Kubernetes (for scaling)
- Prometheus and Grafana (for monitoring)

## 1. Clone the Repository

```bash
git clone https://github.com/repo.git
cd search-engine
```

## 2. Install Dependencies

### Python Dependencies

```bash
pip install -r requirements.txt
```

### Java Dependencies

Compile and package the Java components:

```bash
cd indexing
./gradlew build
```

### Go Dependencies

Install the necessary Go libraries:

```bash
go get ./...
```

## 3. Build Docker Images

Build the Docker images for the search engine components:

```bash
docker-compose build
```

## 4. Start Services

Use Docker Compose to start the services:

```bash
docker-compose up
```

## 5. Verify Setup

Check that the following services are running:

- Web Crawler
- Indexing
- Query Processor
- Ranking

## 6. Run Tests

Execute unit and integration tests:

```bash
pytest tests/
```
