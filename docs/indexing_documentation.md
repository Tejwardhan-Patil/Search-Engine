# Indexing Documentation

## Overview

The indexing system processes and stores crawled content, allowing for fast and efficient keyword lookups.

## Components

1. **Inverted Index Builder (`inverted_index_builder.java`)**
   - Builds an inverted index from the crawled data, mapping keywords to document IDs.
   - Supports sharding for scalability.

2. **Compressed Index (`compressed_index.java`)**
   - Implements compression techniques such as delta encoding to reduce the storage size of the index.

3. **Index File Manager (`index_file_manager.java`)**
   - Manages the storage of index files, handling read/write operations.

4. **Term Frequency Calculator (`term_frequency.java`)**
   - Calculates the frequency of each term in a document.

5. **TF-IDF Calculator (`tfidf_calculator.java`)**
   - Computes the TF-IDF score for terms, which is used for ranking query results.

## Indexing Process

1. **Parsing**: Crawled data is parsed into individual terms.
2. **Frequency Calculation**: Term frequencies are computed for each document.
3. **Inverted Index Creation**: Terms are mapped to document IDs in the inverted index.
4. **Compression**: The index is compressed to save storage space.
5. **Storage**: The compressed index is saved for query processing.
