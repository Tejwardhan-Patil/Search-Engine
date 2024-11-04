#!/bin/bash

# Start the crawling process

# Navigate to the crawler directory
cd ../crawler

# Set up environment variables
export CRAWLER_ENV="production"

# Define log file for the crawling process
LOG_FILE="../logs/crawl_$(date '+%Y%m%d_%H%M%S').log"

# Run crawler_manager.py to start the main crawling process in Python
echo "Starting the crawling process with crawler_manager.py..."
nohup python3 crawler_manager.py >> $LOG_FILE 2>&1 &

# Check if the crawler manager started successfully
if [ $? -eq 0 ]; then
    echo "Crawler Manager started successfully."
else
    echo "Failed to start Crawler Manager." >> $LOG_FILE
    exit 1
fi

# Start the URL queue management process (Go component)
echo "Starting URL queue management..."
nohup go run url_queue.go >> $LOG_FILE 2>&1 &

# Check if the URL queue process started successfully
if [ $? -eq 0 ]; then
    echo "URL Queue Manager started successfully."
else
    echo "Failed to start URL Queue Manager." >> $LOG_FILE
    exit 1
fi

# Log completion of script execution
echo "Crawl started successfully. Logs are being written to $LOG_FILE"