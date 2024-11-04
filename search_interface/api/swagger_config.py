from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Dict

# Function to customize the OpenAPI schema
def custom_openapi(app: FastAPI, title: str, version: str, description: str) -> Dict:
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=title,
        version=version,
        description=description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Main function to configure Swagger
def configure_swagger(app: FastAPI):
    app.openapi = lambda: custom_openapi(
        app,
        title="Search Engine API",
        version="1.0.0",
        description="API documentation for the search engine. Allows users to interact with the search API."
    )
    return app

# Creating the FastAPI app and applying Swagger configuration
def create_app() -> FastAPI:
    app = FastAPI()
    app = configure_swagger(app)
    return app

app = create_app()

# Additional metadata for contact, terms, etc
app.openapi_schema["info"]["contact"] = {
    "name": "Support Team",
    "url": "https://website.com/contact",
    "email": "support@website.com"
}

app.openapi_schema["info"]["license"] = {
    "name": "MIT",
    "url": "https://website.com/license"
}

# Terms of Service link
app.openapi_schema["info"]["termsOfService"] = "https://website.com/terms"

# Tags for the API
app.openapi_schema["tags"] = [
    {
        "name": "search",
        "description": "Operations related to search functionality."
    },
    {
        "name": "results",
        "description": "Operations related to search results retrieval and formatting."
    }
]

# API routes with Swagger tags

@app.get("/search", tags=["search"])
def search_query(query: str):
    """
    Perform a search query.

    - **query**: The search term to query the engine with.
    """
    # Logic for handling the search request
    return {"query": query, "results": []}

@app.get("/results/{query_id}", tags=["results"])
def get_search_results(query_id: str):
    """
    Retrieve results for a specific search query.

    - **query_id**: The ID of the search query.
    """
    # Logic for retrieving and formatting results
    return {"query_id": query_id, "results": []}

# Adding more detailed API responses for the endpoints

@app.get("/search", tags=["search"], responses={
    200: {
        "description": "A list of search results matching the query.",
        "content": {
            "application/json": {
                "example": {
                    "query": "fastapi",
                    "results": [
                        {"title": "FastAPI Documentation", "url": "https://fastapi.tiangolo.com"},
                        {"title": "GitHub Repository", "url": "https://github.com/tiangolo/fastapi"}
                    ]
                }
            }
        }
    },
    404: {"description": "No results found for the search query."}
})
def search(query: str):
    return {"query": query, "results": []}


@app.get("/results/{query_id}", tags=["results"], responses={
    200: {
        "description": "Formatted search results for the given query ID.",
        "content": {
            "application/json": {
                "example": {
                    "query_id": "12345",
                    "results": [
                        {"title": "Result 1", "snippet": "Snippet of the first result."},
                        {"title": "Result 2", "snippet": "Snippet of the second result."}
                    ]
                }
            }
        }
    },
    404: {"description": "No results found for the given query ID."}
})
def get_results(query_id: str):
    return {"query_id": query_id, "results": []}

# Adding external API documentation references

app.openapi_schema["externalDocs"] = {
    "description": "Find more about the API",
    "url": "https://website.com/api-docs"
}

# Models for request and response data

from pydantic import BaseModel
from typing import List

class SearchResult(BaseModel):
    title: str
    url: str

class SearchQueryResponse(BaseModel):
    query: str
    results: List[SearchResult]

# Detailed responses using models

@app.post("/search", response_model=SearchQueryResponse, tags=["search"])
def search_api(query: str):
    """
    Submit a search query and get results.

    - **query**: The search term to be searched.
    """
    return SearchQueryResponse(
        query=query,
        results=[
            SearchResult(title="FastAPI Documentation", url="https://fastapi.tiangolo.com"),
            SearchResult(title="GitHub Repository", url="https://github.com/tiangolo/fastapi")
        ]
    )

# Final schema generation and returning OpenAPI
@app.get("/openapi.json", include_in_schema=False)
def get_openapi_schema():
    return app.openapi()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)