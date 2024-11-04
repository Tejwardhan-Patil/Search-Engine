import os
import hashlib
import logging
from functools import wraps
from flask import Flask, request, jsonify, abort
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuration
API_KEYS = {
    'Person1': 'ea5a6e2b7f8c9d10e11f12a13b14c15d',
    'Person2': 'fa5b7c8d9e0f1a2b3c4d5e6f7g8h9i0j'
}

RATE_LIMIT_WINDOW = timedelta(minutes=1)
MAX_REQUESTS_PER_WINDOW = 5

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('api_auth')

# In-memory rate-limiting tracker
rate_limit_tracker = {}


def rate_limit_check(api_key):
    """Checks the rate limit for a given API key."""
    current_time = datetime.now()
    if api_key not in rate_limit_tracker:
        rate_limit_tracker[api_key] = [current_time]
        return True

    request_times = rate_limit_tracker[api_key]
    # Remove timestamps older than RATE_LIMIT_WINDOW
    request_times = [t for t in request_times if t > current_time - RATE_LIMIT_WINDOW]
    rate_limit_tracker[api_key] = request_times

    if len(request_times) >= MAX_REQUESTS_PER_WINDOW:
        return False
    rate_limit_tracker[api_key].append(current_time)
    return True


def authenticate(api_key):
    """Validates the provided API key."""
    hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
    return any(
        hashlib.sha256(valid_key.encode()).hexdigest() == hashed_key
        for valid_key in API_KEYS.values()
    )


def require_api_key(f):
    """Decorator to enforce API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            logger.warning(f"Unauthorized access attempt. No API key provided.")
            abort(401, description="API key required.")

        if not authenticate(api_key):
            logger.warning(f"Invalid API key used: {api_key}")
            abort(403, description="Invalid API key.")

        if not rate_limit_check(api_key):
            logger.warning(f"Rate limit exceeded for API key: {api_key}")
            abort(429, description="Rate limit exceeded. Try again later.")

        logger.info(f"API key {api_key} authenticated successfully.")
        return f(*args, **kwargs)

    return decorated_function


@app.route('/data', methods=['GET'])
@require_api_key
def get_data():
    """API endpoint to retrieve data."""
    response_data = {
        'status': 'success',
        'message': 'Authenticated request.',
        'data': {'field1': 'value1', 'field2': 'value2'}
    }
    return jsonify(response_data), 200


@app.route('/usage', methods=['GET'])
@require_api_key
def get_usage():
    """Returns current usage stats for the API key."""
    api_key = request.headers.get('X-API-Key')
    request_times = rate_limit_tracker.get(api_key, [])
    current_time = datetime.now()
    requests_in_window = len([t for t in request_times if t > current_time - RATE_LIMIT_WINDOW])

    response_data = {
        'status': 'success',
        'message': 'Usage stats retrieved.',
        'usage': {
            'requests_in_current_window': requests_in_window,
            'max_requests_per_window': MAX_REQUESTS_PER_WINDOW
        }
    }
    return jsonify(response_data), 200


@app.route('/reset_rate_limit', methods=['POST'])
@require_api_key
def reset_rate_limit():
    """Endpoint to manually reset rate limit (for testing purposes)."""
    api_key = request.headers.get('X-API-Key')
    if api_key in rate_limit_tracker:
        rate_limit_tracker[api_key] = []
        logger.info(f"Rate limit reset for API key: {api_key}")
        response_data = {'status': 'success', 'message': 'Rate limit reset.'}
    else:
        response_data = {'status': 'failure', 'message': 'API key not found in tracker.'}

    return jsonify(response_data), 200


@app.errorhandler(401)
def unauthorized_error(error):
    """Handles 401 Unauthorized errors."""
    response = jsonify({'status': 'error', 'message': error.description})
    return response, 401


@app.errorhandler(403)
def forbidden_error(error):
    """Handles 403 Forbidden errors."""
    response = jsonify({'status': 'error', 'message': error.description})
    return response, 403


@app.errorhandler(429)
def rate_limit_error(error):
    """Handles 429 Too Many Requests errors."""
    response = jsonify({'status': 'error', 'message': error.description})
    return response, 429


@app.errorhandler(500)
def internal_server_error(error):
    """Handles 500 Internal Server errors."""
    logger.error(f"Internal server error: {error}")
    response = jsonify({'status': 'error', 'message': 'Internal server error'})
    return response, 500


@app.before_request
def log_request():
    """Logs each request made to the API."""
    api_key = request.headers.get('X-API-Key')
    logger.info(f"Received request to {request.path} with API key: {api_key}")


if __name__ == '__main__':
    # Check if environment variables for API keys exist and update
    env_api_keys = os.getenv('API_KEYS')
    if env_api_keys:
        for person, key in eval(env_api_keys).items():
            API_KEYS[person] = key

    app.run(host='0.0.0.0', port=8080)