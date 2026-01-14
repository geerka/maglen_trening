from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-12345')

ADMIN_PASSWORD = 'maglen2025'
DATA_FILE = 'exercises.json'

# Initialize data file
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Save error: {e}")

# Routes
@app.route('/')
def index():
    exercises = load_data()
    is_admin = session.get('admin', False)
    # Filter exercises: show only visible ones for non-admin, all for admin
    if not is_admin:
        exercises = [e for e in exercises if e.get('visible', True)]
    return render_template('index.html', exercises=exercises, admin=is_admin)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('index'))
        return render_template('admin_login.html', error='Wrong password')
    return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/view/<int:exercise_id>')
def view_exercise(exercise_id):
    exercises = load_data()
    exercise = next((e for e in exercises if e['id'] == exercise_id), None)
    if not exercise:
        return redirect(url_for('index'))
    return render_template('view_exercise.html', exercise=exercise, admin=session.get('admin', False))

@app.route('/add', methods=['GET', 'POST'])
def add_exercise():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        exercises = load_data()
        new_id = max([e['id'] for e in exercises], default=0) + 1
        
        new_exercise = {
            'id': new_id,
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'muscle_groups': request.form.getlist('muscle_groups'),
            'difficulty': request.form.get('difficulty'),
            'video_url': request.form.get('video_url', ''),
            'visible': request.form.get('visible') == 'on',
            'created_at': datetime.now().isoformat()
        }
        exercises.append(new_exercise)
        save_data(exercises)
        return redirect(url_for('index'))
    
    return render_template('add_exercise.html')

@app.route('/edit/<int:exercise_id>', methods=['GET', 'POST'])
def edit_exercise(exercise_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    exercises = load_data()
    exercise = next((e for e in exercises if e['id'] == exercise_id), None)
    if not exercise:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        exercise['name'] = request.form.get('name')
        exercise['description'] = request.form.get('description')
        exercise['muscle_groups'] = request.form.getlist('muscle_groups')
        exercise['difficulty'] = request.form.get('difficulty')
        exercise['video_url'] = request.form.get('video_url', '')
        exercise['visible'] = request.form.get('visible') == 'on'
        save_data(exercises)
        return redirect(url_for('index'))
    
    return render_template('edit_exercise.html', exercise=exercise)

@app.route('/delete/<int:exercise_id>', methods=['POST'])
def delete_exercise(exercise_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    exercises = load_data()
    exercises = [e for e in exercises if e['id'] != exercise_id]
    save_data(exercises)
    return redirect(url_for('index'))

@app.route('/detailed_explanation/<int:exercise_id>')
def detailed_explanation(exercise_id):
    exercises = load_data()
    exercise = next((e for e in exercises if e['id'] == exercise_id), None)
    if not exercise:
        return redirect(url_for('index'))
    return render_template('detailed_explanation.html', exercise=exercise)

@app.route('/edit_detailed_explanation/<int:exercise_id>', methods=['GET', 'POST'])
def edit_detailed_explanation(exercise_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    exercises = load_data()
    exercise = next((e for e in exercises if e['id'] == exercise_id), None)
    if not exercise:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_text':
            text_content = request.form.get('text_content', '')
            if text_content:
                if 'detailed_explanation' not in exercise:
                    exercise['detailed_explanation'] = []
                exercise['detailed_explanation'].append({
                    'type': 'text',
                    'content': text_content
                })
                save_data(exercises)
        
        elif action == 'add_video':
            video_url = request.form.get('video_url', '')
            if video_url:
                if 'detailed_explanation' not in exercise:
                    exercise['detailed_explanation'] = []
                exercise['detailed_explanation'].append({
                    'type': 'video',
                    'content': video_url
                })
                save_data(exercises)
        
        elif action == 'delete_item':
            item_index = int(request.form.get('item_index', -1))
            if 'detailed_explanation' in exercise and 0 <= item_index < len(exercise['detailed_explanation']):
                exercise['detailed_explanation'].pop(item_index)
                save_data(exercises)
        
        return redirect(url_for('edit_detailed_explanation', exercise_id=exercise_id))
    
    return render_template('edit_detailed_explanation.html', exercise=exercise, admin=session.get('admin', False))

@app.route('/toggle-visibility/<int:exercise_id>', methods=['POST'])
def toggle_visibility(exercise_id):
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    exercises = load_data()
    exercise = next((e for e in exercises if e['id'] == exercise_id), None)
    if not exercise:
        return jsonify({'error': 'Exercise not found'}), 404
    
    exercise['visible'] = not exercise.get('visible', True)
    save_data(exercises)
    return jsonify({'visible': exercise['visible']})

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Create uploads/videos directory if it doesn't exist
        uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'videos')
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Save file with timestamp to avoid collisions
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + file.filename
        filepath = os.path.join(uploads_dir, filename)
        
        file.save(filepath)
        
        # Return the relative path for web access
        return jsonify({'location': f'/uploads/videos/{filename}'})
    
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html', exercises=load_data(), admin=session.get('admin', False))

@app.errorhandler(500)
def error(e):
    return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
