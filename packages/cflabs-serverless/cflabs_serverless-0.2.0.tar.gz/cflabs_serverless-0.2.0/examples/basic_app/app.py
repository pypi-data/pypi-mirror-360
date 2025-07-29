"""Basic Flask application example for cflabs-serverless."""

from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "app is live!",
        "timestamp": "2024-01-01T00:00:00Z"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000) 