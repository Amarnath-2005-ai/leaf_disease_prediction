from flask import Flask, render_template, request, redirect, send_from_directory, url_for, flash, jsonify
import numpy as np
import json
import uuid
import tensorflow as tf
import os
import requests
from werkzeug.utils import secure_filename
from tqdm import tqdm

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configuration
UPLOAD_FOLDER = 'uploadimages'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
MODEL_URL = "https://drive.google.com/uc?export=download&id=1HJBCQTyOrTKgBNJ7gH-H9lB37df_81-7"
MODEL_PATH = "models/plant_disease_recog_model_pwp.keras"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("models", exist_ok=True)

def download_file_from_google_drive(file_id, destination):
    """Download a file from Google Drive."""
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768
        total_size = int(response.headers.get('content-length', 0))
        
        with open(destination, "wb") as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading model") as pbar:
                for chunk in response.iter_content(CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

    session = requests.Session()
    response = session.get(MODEL_URL, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(MODEL_URL, params=params, stream=True)

    save_response_content(response, destination)

# Load model with automatic download if missing
try:
    if not os.path.exists(MODEL_PATH):
        print("Model file not found. Downloading from Google Drive...")
        download_file_from_google_drive("1HJBCQTyOrTKgBNJ7gH-H9lB37df_81-7", MODEL_PATH)
        print("Model downloaded successfully!")
    
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Load disease information with error handling
try:
    with open("plant_disease.json", 'r') as file:
        plant_disease = json.load(file)
except Exception as e:
    print(f"Error loading disease information: {e}")
    plant_disease = {}

@app.route('/uploadimages/<path:filename>')
def uploaded_images(filename):
    return send_from_directory('./uploadimages', filename)

@app.route('/', methods=['GET'])
def home():
    return render_template('modern_home.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files():
    """Clean up files older than 1 hour"""
    import time
    current_time = time.time()
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.getmtime(filepath) < current_time - 3600:  # 1 hour
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Error deleting file {filepath}: {e}")

def extract_features(image):
    try:
        image = tf.keras.utils.load_img(image, target_size=(160, 160))
        feature = tf.keras.utils.img_to_array(image)
        feature = np.array([feature])
        return feature
    except Exception as e:
        print(f"Error extracting features: {e}")
        return None

def model_predict(image):
    try:
        img = extract_features(image)
        if img is None:
            return None
        prediction = model.predict(img)
        prediction_label = plant_disease[prediction.argmax()]
        return prediction_label
    except Exception as e:
        print(f"Error making prediction: {e}")
        return None

@app.route('/upload/', methods=['POST', 'GET'])
def uploadimage():
    if request.method == "POST":
        if 'img' not in request.files:
            flash('No file uploaded')
            return redirect('/')
        
        image = request.files['img']
        if image.filename == '':
            flash('No file selected')
            return redirect('/')
        
        if not allowed_file(image.filename):
            flash('Invalid file type. Please upload PNG, JPG, or JPEG')
            return redirect('/')
        
        try:
            filename = secure_filename(image.filename)
            temp_name = f"uploadimages/temp_{uuid.uuid4().hex}"
            full_path = f'{temp_name}_{filename}'
            image.save(full_path)
            
            # Clean up old files
            cleanup_old_files()
            
            prediction = model_predict(f'./{full_path}')
            if prediction is None:
                flash('Error processing image')
                return redirect('/')
                
            return render_template('modern_home.html', 
                                 result=True,
                                 imagepath=f'/{full_path}', 
                                 prediction=prediction)
        except Exception as e:
            flash(f'Error processing image: {str(e)}')
            return redirect('/')
    
    return redirect('/')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True) 