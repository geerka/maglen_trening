from flask import Flask
import os
import json
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key')

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / 'exercises.json'

@app.route('/')
def home():
    return {
        'status': 'ok',
        'message': 'Maglen Fitness API is running',
        'endpoints': {
            'GET /': 'This message',
            'GET /health': 'Health check',
            'GET /api/exercises': 'List all exercises',
            'GET /api/exercise/<id>': 'Get exercise by ID'
        }
    }

@app.route('/health')
def health():
    return {'status': 'healthy'}

@app.route('/api/exercises')
def get_exercises():
    try:
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                exercises = json.load(f)
        else:
            exercises = []
        return {'exercises': exercises, 'count': len(exercises)}
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/exercise/<int:exercise_id>')
def get_exercise(exercise_id):
    try:
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                exercises = json.load(f)
                for ex in exercises:
                    if ex.get('id') == exercise_id:
                        return ex
        return {'error': 'Not found'}, 404
    except Exception as e:
        return {'error': str(e)}, 500

@app.errorhandler(404)
def not_found(e):
    return {'error': 'Not found'}, 404

@app.errorhandler(500)
def server_error(e):
    return {'error': 'Server error'}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
