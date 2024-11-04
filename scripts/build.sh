#!/bin/bash

# Function to check the status of the last command and exit on failure
check_status() {
    if [ $? -ne 0 ]; then
        echo "Error: $1 failed"
        exit 1
    fi
}

# Building the Web Crawler (Python and Go components)
echo "Building Web Crawler components..."
cd ../crawler
echo "Installing Python dependencies..."
pip install -r requirements.txt
check_status "Python dependencies installation"

echo "Building Go components..."
go build -o url_queue url_queue.go
check_status "Go build for url_queue"
go build -o rate_limiting_policy rate_limiting_policy.go
check_status "Go build for rate_limiting_policy"
cd -

# Building the Indexing components (Java)
echo "Building Indexing components..."
cd ../indexing
javac -d bin inverted_index/inverted_index_builder.java
check_status "Java build for inverted_index_builder"
javac -d bin inverted_index/compressed_index.java
check_status "Java build for compressed_index"
javac -d bin index_storage/index_file_manager.java
check_status "Java build for index_file_manager"
javac -d bin index_storage/index_sharding.java
check_status "Java build for index_sharding"
cd -

# Building the Query Processing components (Java and Python)
echo "Building Query Processing components..."
cd ../query_processor
javac -d bin query_parser.java
check_status "Java build for query_parser"
javac -d bin boolean_query_processor.java
check_status "Java build for boolean_query_processor"
javac -d bin phrase_query_processor.java
check_status "Java build for phrase_query_processor"

echo "Installing Python dependencies for query expansion..."
pip install -r requirements.txt
check_status "Python dependencies installation for query expansion"
cd -

# Building the Ranking and Relevance components (Java)
echo "Building Ranking components..."
cd ../ranking
javac -d bin ranking_model.java
check_status "Java build for ranking_model"
javac -d bin pagerank/pagerank_computation.java
check_status "Java build for pagerank_computation"
cd -

# Building the Search Interface (Python)
echo "Building Search Interface..."
cd ../search_interface
echo "Installing Python dependencies..."
pip install -r requirements.txt
check_status "Python dependencies installation"
cd -

# Building the Storage components (Go and Java)
echo "Building Storage components..."
cd ../storage
go build -o document_db document_store/document_db.go
check_status "Go build for document_db"
javac -d bin metadata_store/metadata_manager.java
check_status "Java build for metadata_manager"
cd -

# Building the Distributed Systems components (Go and Java)
echo "Building Distributed Systems components..."
cd ../distributed
go build -o crawler_coordinator distributed_crawling/crawler_coordinator.go
check_status "Go build for crawler_coordinator"
go build -o data_synchronization distributed_crawling/data_synchronization.go
check_status "Go build for data_synchronization"
javac -d bin distributed_indexing/index_partitioning.java
check_status "Java build for index_partitioning"
javac -d bin distributed_indexing/index_merger.java
check_status "Java build for index_merger"
cd -

echo "Build process completed successfully."