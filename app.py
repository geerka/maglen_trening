#!/usr/bin/env python
"""
Maglen Fitness Centre - Flask Web App
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
    level=logging.DEBUG,
    format='[%(levelname)s] %(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("Starting Flask Application")
logger.info("=" * 60)

try:
    from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
    logger.info("✓ Flask imported successfully")
except Exception as e:
    logger.error(f"✗ Failed to import Flask: {e}")
    sys.exit(1)

# Determine base directory
BASE_DIR = Path(__file__).resolve().parent
logger.info(f"Base directory: {BASE_DIR}")

# Create Flask app with explicit paths
try:
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / 'templates'),
        static_folder=str(BASE_DIR / 'static')
    )
    logger.info("✓ Flask app created")
except Exception as e:
    logger.error(f"✗ Failed to create Flask app: {e}")
    sys.exit(1)

# Configure app
try:
    app.config['JSON_SORT_KEYS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
    
    # Secret key
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        secret_key = secrets.token_hex(32)
        logger.warning("No SECRET_KEY in environment. Generated temporary key.")
    app.secret_key = secret_key
    
    logger.info("✓ App configured")
except Exception as e:
    logger.error(f"✗ Failed to configure app: {e}")
    sys.exit(1)

# Setup paths
try:
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        UPLOAD_FOLDER = Path(tempfile.gettempdir()) / 'uploads'
        logger.info("Using temporary directory for uploads (Railway)")
    else:
        UPLOAD_FOLDER = BASE_DIR / 'uploads'
        logger.info("Using local uploads directory")
    
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    (UPLOAD_FOLDER / 'videos').mkdir(exist_ok=True)
    
    app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
    logger.info(f"✓ Upload folder ready: {UPLOAD_FOLDER}")
except Exception as e:
    logger.error(f"✗ Failed to setup upload folder: {e}")
    app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)

# Data file
EXERCISES_FILE = BASE_DIR / 'exercises.json'
ADMIN_PASSWORD = 'maglen2025'

# Initialize data file
try:
    if not EXERCISES_FILE.exists():
        with open(EXERCISES_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        logger.info("✓ Created empty exercises.json")
    else:
        logger.info("✓ exercises.json found")
except Exception as e:
    logger.error(f"✗ Failed to initialize exercises.json: {e}")

# ============================================================================
# Helper Functions
# ============================================================================

def load_exercises():
    """Load exercises from JSON file"""
    try:
        if EXERCISES_FILE.exists():
            with open(EXERCISES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading exercises: {e}")
    return []

def save_exercises(exercises):
    """Save exercises to JSON file"""
    try:
        with open(EXERCISES_FILE, 'w', encoding='utf-8') as f:
            json.dump(exercises, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(exercises)} exercises")
    except Exception as e:
        logger.error(f"Error saving exercises: {e}")

def is_admin():
    """Check if user is admin"""
    return session.get('admin', False)

# ============================================================================
# Routes
# ============================================================================

@app.route('/')
def index():
    """Main page - list of exercises"""
    try:
        exercises = load_exercises()
        admin = is_admin()
        return render_template('index.html', exercises=exercises, admin=admin)
    except Exception as e:
        logger.error(f"Error in index route: {e}", exc_info=True)
        return {'error': f'Server error: {str(e)}'}, 500

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    try:
        if request.method == 'POST':
            password = request.form.get('password')
            if password == ADMIN_PASSWORD:
                session['admin'] = True
                return redirect(url_for('index'))
            else:
                return render_template('admin_login.html', error='Nesprávne heslo!')
        
        return render_template('admin_login.html')
    except Exception as e:
        logger.error(f"Error in admin_login: {e}", exc_info=True)
        return {'error': str(e)}, 500

@app.route('/admin-logout')
def admin_logout():
    """Admin logout"""
    session['admin'] = False
    return redirect(url_for('index'))

@app.route('/uploads/<path:filepath>')
def serve_upload(filepath):
    """Serve uploaded files"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filepath)
    except Exception as e:
        logger.error(f"Error serving upload: {e}")
        return {'error': 'File not found'}, 404

@app.route('/add', methods=['GET', 'POST'])
def add_exercise():
    """Add new exercise"""
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    try:
        if request.method == 'POST':
            exercises = load_exercises()
            
            video_filename = None
            if 'video' in request.files:
                video = request.files['video']
                if video and video.filename != '':
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    video_filename = timestamp + video.filename
                    video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', video_filename)
                    video.save(video_path)
            
            new_exercise = {
                'id': len(exercises) + 1,
                'name': request.form.get('name'),
                'description': request.form.get('description'),
                'muscle_groups': request.form.getlist('muscle_groups'),
                'difficulty': request.form.get('difficulty'),
                'video': video_filename,
                'video_url': request.form.get('video_url', ''),
                'created_at': datetime.now().isoformat()
            }
            
            exercises.append(new_exercise)
            save_exercises(exercises)
            
            return redirect(url_for('index'))
        
        return render_template('add_exercise.html')
    except Exception as e:
        logger.error(f"Error in add_exercise: {e}", exc_info=True)
        return {'error': str(e)}, 500

@app.route('/view/<int:exercise_id>')
def view_exercise(exercise_id):
    """View exercise details"""
    try:
        exercises = load_exercises()
        exercise = next((ex for ex in exercises if ex['id'] == exercise_id), None)
        
        if not exercise:
            return redirect(url_for('index'))
        
        admin = is_admin()
        return render_template('view_exercise.html', exercise=exercise, admin=admin)
    except Exception as e:
        logger.error(f"Error in view_exercise: {e}", exc_info=True)
        return redirect(url_for('index'))

@app.route('/edit/<int:exercise_id>', methods=['GET', 'POST'])
def edit_exercise(exercise_id):
    """Edit exercise"""
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    try:
        exercises = load_exercises()
        exercise = next((ex for ex in exercises if ex['id'] == exercise_id), None)
        
        if not exercise:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            exercise['name'] = request.form.get('name')
            exercise['description'] = request.form.get('description')
            exercise['muscle_groups'] = request.form.getlist('muscle_groups')
            exercise['difficulty'] = request.form.get('difficulty')
            
            if 'video' in request.files:
                video = request.files['video']
                if video and video.filename != '':
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    video_filename = timestamp + video.filename
                    video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', video_filename)
                    video.save(video_path)
                    exercise['video'] = video_filename
            
            if request.form.get('video_url'):
                exercise['video_url'] = request.form.get('video_url')
            
            save_exercises(exercises)
            return redirect(url_for('index'))
        
        return render_template('edit_exercise.html', exercise=exercise)
    except Exception as e:
        logger.error(f"Error in edit_exercise: {e}", exc_info=True)
        return redirect(url_for('index'))

@app.route('/delete/<int:exercise_id>', methods=['POST'])
def delete_exercise(exercise_id):
    """Delete exercise"""
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    try:
        exercises = load_exercises()
        exercise = next((ex for ex in exercises if ex['id'] == exercise_id), None)
        
        if exercise:
            if exercise.get('video'):
                video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', exercise['video'])
                try:
                    if os.path.exists(video_path):
                        os.remove(video_path)
                except:
                    pass
            
            exercises = [ex for ex in exercises if ex['id'] != exercise_id]
            save_exercises(exercises)
        
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error in delete_exercise: {e}", exc_info=True)
        return redirect(url_for('index'))

@app.route('/detailed-explanation/<int:exercise_id>')
def detailed_explanation(exercise_id):
    """View detailed explanation"""
    try:
        exercises = load_exercises()
        exercise = next((ex for ex in exercises if ex['id'] == exercise_id), None)
        
        if not exercise:
            return redirect(url_for('index'))
        
        return render_template('detailed_explanation.html', exercise=exercise)
    except Exception as e:
        logger.error(f"Error in detailed_explanation: {e}", exc_info=True)
        return redirect(url_for('index'))

@app.route('/edit-detailed-explanation/<int:exercise_id>', methods=['GET', 'POST'])
def edit_detailed_explanation(exercise_id):
    """Edit detailed explanation"""
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    try:
        exercises = load_exercises()
        exercise = next((ex for ex in exercises if ex['id'] == exercise_id), None)
        
        if not exercise:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            action = request.form.get('action')
            
            if 'detailed_explanation' not in exercise:
                exercise['detailed_explanation'] = []
            
            if action == 'add_text':
                text_content = request.form.get('text_content')
                if text_content:
                    exercise['detailed_explanation'].append({
                        'type': 'text',
                        'content': text_content
                    })
                video_url = request.form.get('video_url')
                if video_url:
                    exercise['detailed_explanation'].append({
                        'type': 'video',
                        'content': video_url
                    })
            
            elif action == 'delete_item':
                item_index = int(request.form.get('item_index'))
                if 0 <= item_index < len(exercise['detailed_explanation']):
                    exercise['detailed_explanation'].pop(item_index)
            
            save_exercises(exercises)
            return redirect(url_for('edit_detailed_explanation', exercise_id=exercise_id))
        
        admin = is_admin()
        return render_template('edit_detailed_explanation.html', exercise=exercise, admin=admin)
    except Exception as e:
        logger.error(f"Error in edit_detailed_explanation: {e}", exc_info=True)
        return redirect(url_for('index'))

@app.route('/upload-image', methods=['POST'])
def upload_image():
    """Upload image from editor"""
    if not is_admin():
        return {'error': 'Unauthorized'}, 401
    
    try:
        if 'file' not in request.files:
            return {'error': 'No file'}, 400
        
        file = request.files['file']
        if file.filename == '':
            return {'error': 'No filename'}, 400
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', filename)
        file.save(filepath)
        
        return {'location': f'/uploads/videos/{filename}'}
    except Exception as e:
        logger.error(f"Error in upload_image: {e}", exc_info=True)
        return {'error': str(e)}, 500

# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    logger.warning(f"404 Not Found: {request.path}")
    return {'error': 'Not found'}, 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"500 Server Error: {str(e)}", exc_info=True)
    return {'error': 'Internal server error'}, 500

@app.before_request
def before_request():
    logger.debug(f"{request.method} {request.path}")

# ============================================================================
# Health check
# ============================================================================

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'ok', 'message': 'App is running'}

# ============================================================================
# Entry point
# ============================================================================

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_ENV', 'production') == 'development'
        
        logger.info("=" * 60)
        logger.info(f"Starting Flask server on port {port}")
        logger.info(f"Debug mode: {debug}")
        logger.info("=" * 60)
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug,
            threaded=True
        )
    except Exception as e:
        logger.error(f"Failed to start app: {e}", exc_info=True)
        sys.exit(1)
