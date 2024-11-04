from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
import json

app = Flask(__name__)
app.secret_key = 'secret_key'

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Search route for handling search requests
@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    if not query:
        flash('Search query cannot be empty.', 'error')
        return redirect(url_for('index'))

    # API call to the search engine backend
    try:
        response = requests.get(f'http://localhost:5001/api/search', params={'query': query})
        response.raise_for_status()
        results = response.json()
        if not results:
            flash('No results found for your query.', 'info')
        return render_template('results.html', query=query, results=results)
    except requests.exceptions.RequestException as e:
        flash(f'Error connecting to search engine: {e}', 'error')
        return redirect(url_for('index'))

# Route for rendering a detailed view of a search result
@app.route('/details/<int:result_id>')
def details(result_id):
    try:
        response = requests.get(f'http://localhost:5001/api/details/{result_id}')
        response.raise_for_status()
        result_details = response.json()
        return render_template('details.html', result=result_details)
    except requests.exceptions.RequestException as e:
        flash(f'Error retrieving result details: {e}', 'error')
        return redirect(url_for('index'))

# Error handling routes for 404 and 500 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error='404 - Page Not Found'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error='500 - Internal Server Error'), 500

# Route for API status check
@app.route('/status')
def status():
    try:
        response = requests.get(f'http://localhost:5001/api/status')
        response.raise_for_status()
        return jsonify(response.json()), 200
    except requests.exceptions.RequestException as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Helper function to query the API for formatted results
def format_search_results(query):
    try:
        response = requests.get(f'http://localhost:5001/api/search', params={'query': query})
        response.raise_for_status()
        results = response.json()
        return results
    except requests.exceptions.RequestException as e:
        return {'error': f'API request failed: {str(e)}'}

# Adding a static page route for contact information
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Adding a static page route for privacy policy
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

# Route for API-based queries and interaction with the search engine API
@app.route('/api/search', methods=['GET'])
def api_search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is missing'}), 400

    search_results = format_search_results(query)
    return jsonify(search_results), 200

# Route for API-based detailed results
@app.route('/api/details/<int:result_id>', methods=['GET'])
def api_details(result_id):
    try:
        response = requests.get(f'http://localhost:5001/api/details/{result_id}')
        response.raise_for_status()
        result_details = response.json()
        return jsonify(result_details), 200
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

# Route for API status check
@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify({'status': 'running'}), 200

# Static files for handling CSS and JavaScript
@app.route('/static/<path:path>')
def static_file(path):
    return app.send_static_file(path)

# Launch the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)