import subprocess
from query_processor.query_expansion import QueryExpansion

class SearchEngine:
    def __init__(self):
        self.query_expansion = QueryExpansion()

    def search(self, query: str, filters: list = None, sort_by: str = "relevance", page: int = 1, size: int = 10):
        """
        Perform a search query by interacting with the various components of the search engine.
        """
        # Parse the query using Java QueryParser
        parsed_query = self.run_java_query_parser(query)
        
        # Query Expansion (Python)
        expanded_query = self.query_expansion.expand(parsed_query)
        
        # Retrieve document IDs from the index using Java IndexFileManager
        document_ids = self.run_java_index_manager(expanded_query, filters)
        
        # Fetch actual documents from Go-based document storage
        documents = [self.run_go_document_db(doc_id) for doc_id in document_ids]
        
        # Rank the results using Java RankingModel
        ranked_results = self.run_java_ranking_model(documents, sort_by)
        
        # Apply pagination
        start_index = (page - 1) * size
        end_index = start_index + size
        paginated_results = ranked_results[start_index:end_index]
        
        return paginated_results

    def advanced_search(self, query: str, filters: list, sort_by: str = "relevance", page: int = 1, size: int = 10):
        """
        Perform an advanced search with filters.
        """
        return self.search(query, filters, sort_by, page, size)

    def get_status(self):
        """
        Check the status of different components.
        """
        index_status = self.run_java_index_manager_status()
        storage_status = self.run_go_document_db_status()
        query_processor_status = self.run_java_query_parser_status()
        return {
            "index_status": index_status,
            "storage_status": storage_status,
            "query_processor_status": query_processor_status
        }

    def get_search_by_id(self, query_id: str):
        """
        Retrieve a previous search by ID.
        """
        return self.run_java_index_manager_get_search(query_id)
    
    def delete_search(self, query_id: str):
        """
        Delete a saved search by its ID.
        """
        return self.run_java_index_manager_delete_search(query_id)

    def get_suggestions(self, query: str):
        """
        Provide query suggestions based on partial input.
        """
        return self.run_java_query_parser_suggestions(query)
    
    def get_logs(self, limit: int = 100):
        """
        Retrieve the latest search logs for debugging purposes.
        """
        return self.run_java_index_manager_get_logs(limit)

    # Java-based Query Parser subprocess communication
    def run_java_query_parser(self, query: str):
        command = ["java", "-cp", "query_processor/QueryParserMain", "QueryParserMain", query]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error in QueryParser: {result.stderr}")
        return result.stdout.strip()

    def run_java_query_parser_status(self):
        command = ["java", "-cp", "query_processor/QueryParserMain", "QueryParserMain", "status"]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error in QueryParser status: {result.stderr}")
        return result.stdout.strip()

    def run_java_query_parser_suggestions(self, query: str):
        command = ["java", "-cp", "query_processor/QueryParserMain", "QueryParserMain", "suggestions", query]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error in QueryParser suggestions: {result.stderr}")
        return result.stdout.strip()

    # Java-based Index Manager subprocess communication
    def run_java_index_manager(self, query: str, filters: list):
        command = ["java", "-cp", "indexing/index_storage/IndexFileManager", "IndexFileManager", query] + filters
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error in IndexFileManager: {result.stderr}")
        return result.stdout.strip().splitlines() 

    def run_java_index_manager_get_search(self, query_id: str):
        command = ["java", "-cp", "indexing/index_storage/IndexFileManager", "IndexFileManager", "get", query_id]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error in IndexFileManager get_search: {result.stderr}")
        return result.stdout.strip()

    def run_java_index_manager_delete_search(self, query_id: str):
        command = ["java", "-cp", "indexing/index_storage/IndexFileManager", "IndexFileManager", "delete", query_id]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error in IndexFileManager delete_search: {result.stderr}")
        return result.stdout.strip()

    def run_java_index_manager_status(self):
        command = ["java", "-cp", "indexing/index_storage/IndexFileManager", "IndexFileManager", "status"]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error in IndexFileManager status: {result.stderr}")
        return result.stdout.strip()

    def run_java_index_manager_get_logs(self, limit: int):
        command = ["java", "-cp", "indexing/index_storage/IndexFileManager", "IndexFileManager", "logs", str(limit)]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error in IndexFileManager get_logs: {result.stderr}")
        return result.stdout.strip().splitlines()

    # Go-based Document Storage subprocess communication
    def run_go_document_db(self, doc_id: str):
        command = ["go", "run", "storage/document_store/document_db.go", doc_id]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error in DocumentDB: {result.stderr}")
        return result.stdout.strip()

    def run_go_document_db_status(self):
        command = ["go", "run", "storage/document_store/document_db.go", "status"]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error in DocumentDB status: {result.stderr}")
        return result.stdout.strip()

    # Java-based Ranking Model subprocess communication
    def run_java_ranking_model(self, documents: list, sort_by: str):
        command = ["java", "-cp", "ranking/RankingModel", "RankingModel", sort_by] + documents
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error in RankingModel: {result.stderr}")
        return result.stdout.strip().splitlines()

    # Java-based Relevance Feedback subprocess communication
    def run_java_relevance_feedback(self, feedback_data: str):
        command = ["java", "-cp", "ranking/RelevanceFeedback", "RelevanceFeedback", feedback_data]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error in RelevanceFeedback: {result.stderr}")
        return result.stdout.strip()