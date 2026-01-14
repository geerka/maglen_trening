from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# ADMIN HESLO - ZMEŇ NA SVOJE
ADMIN_PASSWORD = 'maglen2025'

# Vytvor uploads folder ak neexistuje
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'), exist_ok=True)

# File pre ukladanie cvikov
EXERCISES_FILE = 'exercises.json'

def load_exercises():
    """Načítaj cviky z JSON súboru"""
    if os.path.exists(EXERCISES_FILE):
        with open(EXERCISES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_exercises(exercises):
    """Ulož cviky do JSON súboru"""
    with open(EXERCISES_FILE, 'w', encoding='utf-8') as f:
        json.dump(exercises, f, ensure_ascii=False, indent=2)

def is_admin():
    """Kontrola či je používateľ admin"""
    return session.get('admin', False)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin prihlásenie"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('index'))
        else:
            return render_template('admin_login.html', error='Nesprávne heslo!')
    
    return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    """Admin odhlásenie"""
    session['admin'] = False
    return redirect(url_for('index'))

@app.route('/uploads/<path:filepath>')
def serve_upload(filepath):
    """Servuj uploadované súbory (obrázky, videá)"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filepath)
    except:
        return {'error': 'File not found'}, 404

@app.route('/')
def index():
    """Hlavná stránka s listom cvikov"""
    exercises = load_exercises()
    admin = is_admin()
    return render_template('index.html', exercises=exercises, admin=admin)

@app.route('/add', methods=['GET', 'POST'])
def add_exercise():
    """Pridaj nový cvik"""
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        exercises = load_exercises()
        
        # Spracuj video súbor
        video_filename = None
        if 'video' in request.files:
            video = request.files['video']
            if video and video.filename != '':
                # Vytvor jedinečný názov súboru
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                video_filename = timestamp + video.filename
                video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', video_filename)
                video.save(video_path)
        
        # Vytvor nový cvik
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

@app.route('/api/exercise/<int:exercise_id>/detailed-explanation', methods=['GET'])
def api_get_detailed_explanation(exercise_id):
    """GET API - Získaj detailné vysvetlenie cviku"""
    exercises = load_exercises()
    exercise = next((ex for ex in exercises if ex['id'] == exercise_id), None)
    
    if not exercise:
        return {'error': 'Exercise not found'}, 404
    
    return {
        'exercise_id': exercise_id,
        'exercise_name': exercise.get('name'),
        'detailed_explanation': exercise.get('detailed_explanation', [])
    }

@app.route('/api/exercise/<int:exercise_id>/detailed-explanation', methods=['POST'])
def api_add_detailed_explanation(exercise_id):
    """POST API - Pridaj obsah do detailného vysvetlenia"""
    if not is_admin():
        return {'error': 'Unauthorized'}, 401
    
    exercises = load_exercises()
    exercise = next((ex for ex in exercises if ex['id'] == exercise_id), None)
    
    if not exercise:
        return {'error': 'Exercise not found'}, 404
    
    data = request.get_json()
    
    if 'type' not in data or 'content' not in data:
        return {'error': 'Missing type or content'}, 400
    
    if 'detailed_explanation' not in exercise:
        exercise['detailed_explanation'] = []
    
    item_type = data.get('type')  # 'text', 'image', 'video'
    
    if item_type == 'text':
        exercise['detailed_explanation'].append({
            'type': 'text',
            'content': data.get('content')
        })
    elif item_type == 'image':
        exercise['detailed_explanation'].append({
            'type': 'image',
            'content': data.get('content'),
            'caption': data.get('caption', '')
        })
    elif item_type == 'video':
        exercise['detailed_explanation'].append({
            'type': 'video',
            'content': data.get('content')
        })
    else:
        return {'error': 'Invalid type'}, 400
    
    save_exercises(exercises)
    
    return {
        'success': True,
        'message': 'Content added',
        'item_index': len(exercise['detailed_explanation']) - 1
    }, 201

@app.route('/api/exercise/<int:exercise_id>/detailed-explanation/<int:item_index>', methods=['DELETE'])
def api_delete_detailed_explanation(exercise_id, item_index):
    """DELETE API - Vymaž obsah z detailného vysvetlenia"""
    if not is_admin():
        return {'error': 'Unauthorized'}, 401
    
    exercises = load_exercises()
    exercise = next((ex for ex in exercises if ex['id'] == exercise_id), None)
    
    if not exercise:
        return {'error': 'Exercise not found'}, 404
    
    explanation = exercise.get('detailed_explanation', [])
    
    if not (0 <= item_index < len(explanation)):
        return {'error': 'Invalid item index'}, 400
    
    explanation.pop(item_index)
    save_exercises(exercises)
    
    return {'success': True, 'message': 'Content deleted'}

@app.route('/api/exercise/<int:exercise_id>/detailed-explanation/<int:item_index>', methods=['PUT'])
def api_update_detailed_explanation(exercise_id, item_index):
    """PUT API - Uprav obsah detailného vysvetlenia"""
    if not is_admin():
        return {'error': 'Unauthorized'}, 401
    
    exercises = load_exercises()
    exercise = next((ex for ex in exercises if ex['id'] == exercise_id), None)
    
    if not exercise:
        return {'error': 'Exercise not found'}, 404
    
    explanation = exercise.get('detailed_explanation', [])
    
    if not (0 <= item_index < len(explanation)):
        return {'error': 'Invalid item index'}, 400
    
    data = request.get_json()
    item = explanation[item_index]
    
    if 'content' in data:
        item['content'] = data['content']
    if 'caption' in data and item['type'] == 'image':
        item['caption'] = data['caption']
    
    save_exercises(exercises)
    
    return {'success': True, 'message': 'Content updated', 'item': item}

@app.route('/upload-image', methods=['POST'])
def upload_image():
    """Upload obrázka z editora"""
    if not is_admin():
        return {'error': 'Unauthorized'}, 401
    
    if 'file' not in request.files:
        return {'error': 'No file'}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {'error': 'No filename'}, 400
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', filename)
        file.save(filepath)
        
        return {'location': f'/uploads/videos/{filename}'}
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/edit/<int:exercise_id>', methods=['GET', 'POST'])
def edit_exercise(exercise_id):
    """Uprav existujúci cvik"""
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    exercises = load_exercises()
    exercise = next((ex for ex in exercises if ex['id'] == exercise_id), None)
    
    if not exercise:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Aktualizuj cvik
        exercise['name'] = request.form.get('name')
        exercise['description'] = request.form.get('description')
        exercise['muscle_groups'] = request.form.getlist('muscle_groups')
        exercise['difficulty'] = request.form.get('difficulty')
        
        # Ak je nové video
        if 'video' in request.files:
            video = request.files['video']
            if video and video.filename != '':
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                video_filename = timestamp + video.filename
                video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', video_filename)
                video.save(video_path)
                exercise['video'] = video_filename
        
        # Ak je externe video URL
        if request.form.get('video_url'):
            exercise['video_url'] = request.form.get('video_url')
        
        save_exercises(exercises)
        return redirect(url_for('index'))
    
    return render_template('edit_exercise.html', exercise=exercise)

@app.route('/delete/<int:exercise_id>', methods=['POST'])
def delete_exercise(exercise_id):
    """Vymaž cvik"""
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    exercises = load_exercises()
    exercise = next((ex for ex in exercises if ex['id'] == exercise_id), None)
    
    if exercise:
        # Vymaž video súbor ak existuje
        if exercise.get('video'):
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', exercise['video'])
            if os.path.exists(video_path):
                os.remove(video_path)
        
        exercises = [ex for ex in exercises if ex['id'] != exercise_id]
        save_exercises(exercises)
    
    return redirect(url_for('index'))

@app.route('/view/<int:exercise_id>')
def view_exercise(exercise_id):
    """Zobraz detail cviku"""
    exercises = load_exercises()
    exercise = next((ex for ex in exercises if ex['id'] == exercise_id), None)
    
    if not exercise:
        return redirect(url_for('index'))
    
    admin = is_admin()
    return render_template('view_exercise.html', exercise=exercise, admin=admin)

@app.route('/detailed-explanation/<int:exercise_id>')
def detailed_explanation(exercise_id):
    """Zobraz detailné vysvetlenie cviku"""
    exercises = load_exercises()
    exercise = next((ex for ex in exercises if ex['id'] == exercise_id), None)
    
    if not exercise:
        return redirect(url_for('index'))
    
    return render_template('detailed_explanation.html', exercise=exercise)

@app.route('/edit-detailed-explanation/<int:exercise_id>', methods=['GET', 'POST'])
def edit_detailed_explanation(exercise_id):
    """Uprav detailné vysvetlenie cviku"""
    if not is_admin():
        return redirect(url_for('admin_login'))
    
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

if __name__ == '__main__':
    app.run(debug=True)
