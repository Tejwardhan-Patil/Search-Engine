# Base image for multi-stage builds

# Build Java components
FROM openjdk:17-jdk-alpine as java-builder

# Set the working directory for Java build
WORKDIR /app

# Copy the Java source code
COPY indexing/ ./indexing/
COPY query_processor/ ./query_processor/
COPY ranking/ ./ranking/
COPY storage/ ./storage/
COPY distributed/ ./distributed/

# Compile the Java components
RUN javac ./indexing/inverted_index/*.java ./query_processor/*.java ./ranking/*.java ./storage/*.java ./distributed/*.java

# Build Go components
FROM golang:1.19-alpine as go-builder

# Set the working directory for Go build
WORKDIR /app

# Copy the Go source code
COPY crawler/ ./crawler/
COPY storage/document_store/ ./document_store/
COPY distributed/ ./distributed/
COPY monitoring/ ./monitoring/

# Build Go components
RUN go build ./crawler/url_queue.go ./storage/document_store/document_db.go ./distributed/crawler_coordinator.go ./monitoring/prometheus_exporter.go

# Build Python components
FROM python:3.11-slim as python-builder

# Set working directory
WORKDIR /app

# Install necessary Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy Python source code
COPY crawler/ ./crawler/
COPY search_interface/ ./search_interface/
COPY monitoring/ ./monitoring/

# Ensure proper permissions for Python scripts
RUN chmod +x ./search_interface/app.py

# Final stage to assemble the entire application
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    golang \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy compiled files from previous stages
COPY --from=java-builder /app/indexing /app/indexing
COPY --from=java-builder /app/query_processor /app/query_processor
COPY --from=java-builder /app/ranking /app/ranking
COPY --from=java-builder /app/storage /app/storage
COPY --from=java-builder /app/distributed /app/distributed
COPY --from=go-builder /app/crawler /app/crawler
COPY --from=go-builder /app/document_store /app/document_store
COPY --from=python-builder /app/crawler /app/crawler
COPY --from=python-builder /app/search_interface /app/search_interface
COPY --from=python-builder /app/monitoring /app/monitoring

# Copy necessary configuration and deployment scripts
COPY configs/ /app/configs/
COPY scripts/ /app/scripts/
COPY deployment/docker/docker-compose.yml /app/docker-compose.yml

# Set environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$PATH:/usr/local/go/bin

# Run the setup script
RUN chmod +x ./scripts/build.sh && ./scripts/build.sh

# Expose necessary ports
EXPOSE 8080 9090 3000

# Start the application
CMD ["./scripts/deploy.sh"]