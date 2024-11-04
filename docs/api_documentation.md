# Search Engine API Documentation

## Base URL

`https://website.com/api`

## Endpoints

### 1. Search Query

- **Endpoint**: `/search`
- **Method**: `POST`
- **Description**: Submit a search query and retrieve results.
- **Request Body**:

    ```json
    {
        "query": "search terms",
        "filters": {
            "date_range": "last_30_days",
            "language": "en"
        }
    }
    ```

- **Response**:
  
    ```json
    {
        "results": [
            {
                "title": "Page Title",
                "url": "https://website.com/page",
                "snippet": "This is a sample snippet of the page."
            }
        ],
        "total_results": 1024
    }
    ```

### 2. Fetch Document Metadata

- **Endpoint**: `/document/{id}`
- **Method**: `GET`
- **Description**: Retrieve metadata for a specific document by its ID.
- **Response**:

    ```json
    {
        "id": "123456",
        "url": "https://website.com/page",
        "title": "Document Title",
        "metadata": {
            "author": "Person",
            "publish_date": "2024-09-01"
        }
    }
    ```

### 3. Get API Documentation (Swagger)

- **Endpoint**: `/docs`
- **Method**: `GET`
- **Description**: Retrieve API documentation in Swagger format.
- **Response**: Swagger UI or JSON description of API.
