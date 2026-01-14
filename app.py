#!/usr/bin/env python
"""
Maglen Fitness Centre - Minimal Flask App (JSON API only)
"""

import os
import sys
import json
import tempfile
import secrets
from datetime import datetime
from pathlib import Path

# Configure logging FIRST
import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("STARTING MAGLEN FITNESS APP")
print("="*70 + "\n")

# Import Flask
try:
    from flask import Flask, jsonify, request, session
    print("✓ Flask imported")
except Exception as e:
    print(f"✗ Flask import failed: {e}")
    sys.exit(1)

# Setup directories
BASE_DIR = Path(__file__).resolve().parent
print(f"✓ Base dir: {BASE_DIR}")

# Create app - MINIMAL
try:
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
    
    secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    app.secret_key = secret_key
    
    print("✓ Flask app created and configured")
except Exception as e:
    print(f"✗ Failed to create app: {e}")
    sys.exit(1)

# Setup upload folder
try:
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        UPLOAD_FOLDER = Path(tempfile.gettempdir()) / 'uploads'
        print(f"✓ Using temp dir: {UPLOAD_FOLDER}")
    else:
        UPLOAD_FOLDER = BASE_DIR / 'uploads'
        print(f"✓ Using local dir: {UPLOAD_FOLDER}")
    
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    (UPLOAD_FOLDER / 'videos').mkdir(exist_ok=True)
    app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
except Exception as e:
    print(f"✗ Upload folder setup failed: {e}")
    sys.exit(1)

# Data file
EXERCISES_FILE = BASE_DIR / 'exercises.json'
ADMIN_PASSWORD = 'maglen2025'

try:
    if not EXERCISES_FILE.exists():
        with open(EXERCISES_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
    print(f"✓ Data file: {EXERCISES_FILE}")
except Exception as e:
    print(f"✗ Data file init failed: {e}")
    sys.exit(1)

# ============================================================================
# Data functions
# ============================================================================

def load_exercises():
    try:
        if EXERCISES_FILE.exists():
            with open(EXERCISES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Load error: {e}")
    return []

def save_exercises(exercises):
    try:
        with open(EXERCISES_FILE, 'w', encoding='utf-8') as f:
            json.dump(exercises, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Save error: {e}")

def is_admin():
    return session.get('admin', False)

# ============================================================================
# Routes
# ============================================================================

@app.route('/')
def index():
    """Test endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Maglen Fitness API',
        'version': '1.0',
        'endpoints': [
            'GET /health',
            'GET /api/exercises',
            'POST /api/admin-login',
            'POST /api/exercise/add',
            'GET /api/exercise/<id>',
            'POST /api/exercise/<id>/edit',
            'POST /api/exercise/<id>/delete'
        ]
    })

@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'healthy'})

@app.route('/api/exercises')
def get_exercises():
    """Get all exercises"""
    try:
        exercises = load_exercises()
        return jsonify({'exercises': exercises, 'count': len(exercises)})
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/exercise/<int:exercise_id>')
def get_exercise(exercise_id):
    """Get single exercise"""
    try:
        exercises = load_exercises()
        exercise = next((ex for ex in exercises if ex['id'] == exercise_id), None)
        
        if not exercise:
            return jsonify({'error': 'Not found'}), 404
        
        return jsonify(exercise)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin-login', methods=['POST'])
def admin_login():
    """Admin login"""
    try:
        data = request.get_json()
        password = data.get('password')
        
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return jsonify({'success': True, 'message': 'Logged in'})
        else:
            return jsonify({'success': False, 'message': 'Wrong password'}), 401
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin-logout', methods=['POST'])
def admin_logout():
    """Admin logout"""
    session['admin'] = False
    return jsonify({'success': True, 'message': 'Logged out'})

@app.route('/api/exercise/add', methods=['POST'])
def add_exercise():
    """Add exercise"""
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        exercises = load_exercises()
        
        new_exercise = {
            'id': len(exercises) + 1,
            'name': data.get('name'),
            'description': data.get('description'),
            'muscle_groups': data.get('muscle_groups', []),
            'difficulty': data.get('difficulty'),
            'video': data.get('video'),
            'video_url': data.get('video_url', ''),
            'created_at': datetime.now().isoformat()
        }
        
        exercises.append(new_exercise)
        save_exercises(exercises)
        
        return jsonify({'success': True, 'exercise': new_exercise}), 201
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/exercise/<int:exercise_id>/edit', methods=['POST'])
def edit_exercise(exercise_id):
    """Edit exercise"""
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        exercises = load_exercises()
        exercise = next((ex for ex in exercises if ex['id'] == exercise_id), None)
        
        if not exercise:
            return jsonify({'error': 'Not found'}), 404
        
        exercise['name'] = data.get('name', exercise['name'])
        exercise['description'] = data.get('description', exercise['description'])
        exercise['muscle_groups'] = data.get('muscle_groups', exercise['muscle_groups'])
        exercise['difficulty'] = data.get('difficulty', exercise['difficulty'])
        
        save_exercises(exercises)
        return jsonify({'success': True, 'exercise': exercise})
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/exercise/<int:exercise_id>/delete', methods=['POST'])
def delete_exercise(exercise_id):
    """Delete exercise"""
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        exercises = load_exercises()
        exercises = [ex for ex in exercises if ex['id'] != exercise_id]
        save_exercises(exercises)
        
        return jsonify({'success': True, 'message': 'Deleted'})
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Error handlers
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"500 Error: {e}", exc_info=True)
    return jsonify({'error': 'Server error'}), 500

# ============================================================================
# Start app
# ============================================================================

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_ENV', 'production') == 'development'
        
        print("\n" + "="*70)
        print(f"STARTING SERVER on port {port} (debug={debug})")
        print("="*70 + "\n")
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug,
            threaded=True
        )
    except Exception as e:
        print(f"✗ Failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
