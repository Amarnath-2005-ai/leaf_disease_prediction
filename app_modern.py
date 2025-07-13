from flask import Flask, render_template, request, redirect, send_from_directory, flash
import numpy as np
import json
import uuid
import tensorflow as tf
import os
import time
import gdown
import shutil
from tqdm import tqdm
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Config
UPLOAD_FOLDER = 'uploadimages'
MODEL_FOLDER = 'models'
MODEL_PATH = os.path.join(MODEL_FOLDER, "plant_disease_recog_model_pwp.keras")
MODEL_FILE_ID = "1HJBCQTyOrTKgBNJ7gH-H9lB37df_81-7"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)

# 🔄 Clean the upload folder on start
def clean_upload_folder_on_start():
    folder = os.path.abspath(UPLOAD_FOLDER)
    if not os.path.exists(folder):
        print(f"[Startup Cleanup] Folder not found: {folder}")
        return

    deleted = 0
    for root, dirs, files in os.walk(folder, topdown=False):
        for name in files:
            path = os.path.join(root, name)
            try:
                os.remove(path)
                print(f"[Startup Cleanup] Deleted file: {path}")
                deleted += 1
            except Exception as e:
                print(f"[Startup Cleanup] Error deleting file: {e}")

        for name in dirs:
            path = os.path.join(root, name)
            try:
                shutil.rmtree(path)
                print(f"[Startup Cleanup] Deleted folder: {path}")
                deleted += 1
            except Exception as e:
                print(f"[Startup Cleanup] Error deleting folder: {e}")

    print(f"[Startup Cleanup] Done. Total items deleted: {deleted}")

# 📥 Download the model using gdown with a progress bar
def download_model_with_gdown(file_id, destination):
    try:
        url = f"https://drive.google.com/uc?id={file_id}"
        print("[Model Download] Downloading model from Google Drive...")
        gdown.download(url, destination, quiet=False)
        return os.path.exists(destination)
    except Exception as e:
        print(f"[Model Download] Error: {e}")
        return False

# 🧠 Load model
try:
    if not os.path.exists(MODEL_PATH):
        success = download_model_with_gdown(MODEL_FILE_ID, MODEL_PATH)
        if not success:
            raise Exception("Model download failed")

    print("[Model] Loading...")
    model = tf.keras.models.load_model(MODEL_PATH)
    print("[Model] Loaded successfully!")
except Exception as e:
    print(f"[Model] Error loading model: {e}")
    model = None

# 🌿 Load disease labels
try:
    with open("plant_disease.json", 'r') as f:
        plant_disease = json.load(f)
except Exception as e:
    print(f"[Error] Loading disease labels failed: {e}")
    plant_disease = {}

# 🖼️ Serve uploaded image files
@app.route('/uploadimages/<path:filename>')
def uploaded_images(filename):
    return send_from_directory('./uploadimages', filename)

# 🏠 Home page
@app.route('/')
def home():
    return render_template('modern_home.html')

# ✅ File type check
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 🧹 Remove files older than 1 hour
def cleanup_old_files():
    now = time.time()
    for f in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, f)
        if os.path.isfile(path) and os.path.getmtime(path) < now - 3600:
            try:
                os.remove(path)
            except Exception as e:
                print(f"[Cleanup] Error deleting old file: {e}")

# 🧬 Extract image features
def extract_features(image_path):
    try:
        image = tf.keras.utils.load_img(image_path, target_size=(160, 160))
        feature = tf.keras.utils.img_to_array(image)
        feature = np.expand_dims(feature, axis=0)
        return feature
    except Exception as e:
        print(f"[Feature Extraction] Error: {e}")
        return None

# 🤖 Predict using the model
def model_predict(image_path):
    try:
        img = extract_features(image_path)
        if img is None:
            return None
        pred = model.predict(img)
        label = plant_disease[pred.argmax()]
        return label
    except Exception as e:
        print(f"[Prediction] Error: {e}")
        return None

# 📤 Upload endpoint
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
            flash('Invalid file type')
            return redirect('/')

        try:
            filename = secure_filename(image.filename)
            unique_name = f"temp_{uuid.uuid4().hex}_{filename}"
            full_path = os.path.join(UPLOAD_FOLDER, unique_name)
            image.save(full_path)

            cleanup_old_files()
            prediction = model_predict(full_path)

            if prediction is None:
                flash('Prediction failed')
                return redirect('/')

            return render_template('modern_home.html',
                                   result=True,
                                   imagepath=f'/uploadimages/{unique_name}',
                                   prediction=prediction)
        except Exception as e:
            flash(f'Error processing image: {str(e)}')
            return redirect('/')

    return redirect('/')

# 🚀 Start server
if __name__ == "__main__":
    clean_upload_folder_on_start()
    app.run(host='127.0.0.1', port=5000, debug=True)
