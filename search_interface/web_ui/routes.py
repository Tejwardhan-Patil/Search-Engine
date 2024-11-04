from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from search_interface.api.search_api import search_query
from search_interface.api.results_formatter import format_results
import csv
from io import StringIO

app = Flask(__name__)

# Home route - displays the search page
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Search route - handles search queries
@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    
    if not query:
        return redirect(url_for("index", error="Please enter a query."))

    try:
        # Perform the search using the search API
        raw_results = search_query(query)
        results = format_results(raw_results)

        return render_template("results.html", results=results, query=query)

    except Exception as e:
        print(f"Error processing search query: {e}")
        return redirect(url_for("error_500"))

# Error route for 404 not found
@app.errorhandler(404)
def error_404(error):
    return render_template("error.html", error="Page Not Found"), 404

# Error route for 500 internal server error
@app.errorhandler(500)
def error_500(error=None):
    return render_template("error.html", error="Internal Server Error"), 500

# API route for search query submission (JSON format)
@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.get_json()

    if not data or "query" not in data:
        return jsonify({"error": "Invalid query."}), 400

    query = data["query"]

    try:
        # Call the API to execute the search
        raw_results = search_query(query)
        formatted_results = format_results(raw_results)

        return jsonify({"results": formatted_results, "query": query})

    except Exception as e:
        print(f"API error while processing query: {e}")
        return jsonify({"error": "Search query failed."}), 500

# API route to fetch suggestions (JSON format)
@app.route("/api/suggestions", methods=["GET"])
def api_suggestions():
    query = request.args.get("query")

    if not query:
        return jsonify({"error": "Query not provided."}), 400

    try:
        suggestions = get_suggestions(query)
        return jsonify({"suggestions": suggestions})

    except Exception as e:
        print(f"Error fetching suggestions: {e}")
        return jsonify({"error": "Failed to retrieve suggestions."}), 500

# Route for search result filtering based on relevance or other criteria
@app.route("/filter", methods=["POST"])
def filter_results():
    query = request.form.get("query")
    filter_type = request.form.get("filter")

    if not query or not filter_type:
        return redirect(url_for("index", error="Missing query or filter criteria."))

    try:
        # Call the search API with the filter criteria
        raw_results = search_query(query, filter_type=filter_type)
        results = format_results(raw_results)

        return render_template("results.html", results=results, query=query)

    except Exception as e:
        print(f"Error filtering search results: {e}")
        return redirect(url_for("error_500"))

# Helper route for autocomplete suggestions
@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    query = request.args.get("query")

    if not query:
        return jsonify({"error": "Query parameter is missing."}), 400

    try:
        suggestions = get_autocomplete_suggestions(query)
        return jsonify(suggestions)

    except Exception as e:
        print(f"Error fetching autocomplete: {e}")
        return jsonify({"error": "Autocomplete failed."}), 500

# Route for search result pagination
@app.route("/search/page/<int:page_number>", methods=["GET"])
def search_pagination(page_number):
    query = request.args.get("query")

    if not query:
        return redirect(url_for("index", error="Please provide a query."))

    try:
        # Fetch paginated results from the search API
        raw_results = search_query(query, page=page_number)
        results = format_results(raw_results)

        return render_template("results.html", results=results, query=query, page=page_number)

    except Exception as e:
        print(f"Error fetching paginated results: {e}")
        return redirect(url_for("error_500"))

# Downloadable CSV for search results
@app.route("/search/download", methods=["GET"])
def download_results():
    query = request.args.get("query")

    if not query:
        return redirect(url_for("index", error="Please provide a query."))

    try:
        # Execute search and format results
        raw_results = search_query(query)
        results = format_results(raw_results)

        # Convert results to CSV
        csv_data = convert_to_csv(results)
        response = make_response(csv_data)
        response.headers["Content-Disposition"] = f"attachment; filename=search_results.csv"
        response.headers["Content-Type"] = "text/csv"

        return response

    except Exception as e:
        print(f"Error downloading results: {e}")
        return redirect(url_for("error_500"))

# Function for converting search results to CSV format
def convert_to_csv(results):
    output = StringIO()
    writer = csv.writer(output)

    # Write headers
    writer.writerow(["Title", "URL", "Snippet"])

    # Write each result
    for result in results:
        writer.writerow([result["title"], result["url"], result["snippet"]])

    return output.getvalue()

# Route for advanced search options
@app.route("/advanced_search", methods=["GET", "POST"])
def advanced_search():
    if request.method == "POST":
        query = request.form.get("query")
        filter_type = request.form.get("filter")

        if not query:
            return redirect(url_for("index", error="Please enter a query."))

        try:
            # Perform advanced search with filters
            raw_results = search_query(query, filter_type=filter_type)
            results = format_results(raw_results)

            return render_template("results.html", results=results, query=query)

        except Exception as e:
            print(f"Error processing advanced search: {e}")
            return redirect(url_for("error_500"))

    return render_template("advanced_search.html")

# Start the Flask application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

# Function to simulate getting suggestions for query expansion or autocomplete
def get_suggestions(query):
    # Function sto be integrated with the API or database to fetch suggestions.
    return ["Suggestion 1", "Suggestion 2", "Suggestion 3"]

# Function to simulate getting autocomplete suggestions
def get_autocomplete_suggestions(query):
    # Function to be integrated with the API or service providing autocomplete.
    return {"suggestions": ["Auto1", "Auto2", "Auto3"]}