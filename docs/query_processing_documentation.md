# Query Processing Documentation

This document explains the components and flow of the query processing pipeline used in the search engine.

## 1. Overview

Query processing is responsible for interpreting user queries and translating them into a format that can be understood by the search engine. It also applies techniques to enhance the quality of search results.

### Core Components

- **Query Parser**: Breaks down user input into tokens and constructs a query tree.
- **Query Expansion**: Enhances the query by adding related terms or handling misspellings.
- **Boolean Query Processor**: Handles logical queries with `AND`, `OR`, and `NOT`.
- **Phrase Query Processor**: Supports exact phrase matching.
- **Fuzzy Query Processor**: Implements approximate matching for handling typos or near matches.
- **Query Rewriter**: Optimizes queries by transforming or simplifying them.

## 2. Query Flow

1. **User Input**: Users submit queries via the search interface.
2. **Query Parsing**: The `query_parser.java` parses the input into tokens and constructs a query tree.
3. **Query Expansion**: Using `query_expansion.py`, synonyms, and corrections are applied to broaden the scope.
4. **Query Processing**: Depending on the type of query (Boolean, phrase, or fuzzy), the respective processors (`boolean_query_processor.java`, `phrase_query_processor.java`, `fuzzy_query_processor.java`) handle the interpretation.
5. **Ranking**: Once results are retrieved, they are ranked using relevance algorithms.
6. **Results Formatting**: The results are formatted for display via the search interface.

## 3. Optimization Techniques

- **Stemming and Lemmatization**: Performed during query rewriting to standardize word forms.
- **Synonym Expansion**: Adds alternate terms to the query for broader matching.
- **Spell Correction**: Identifies and corrects misspelled words.

## 4. Error Handling

- **Syntax Errors**: If the query has invalid syntax, the parser will reject it.
- **Unrecognized Terms**: If no results are found, the query expansion component may be triggered to suggest alternatives.

## 5. Unit Testing

Tests for query processing components can be found in `tests/QueryProcessingTests.java`.
