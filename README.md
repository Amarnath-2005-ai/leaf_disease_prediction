# Plant Disease Detection 🌿

A Flask web application that detects plant diseases from leaf images using deep learning.

## Quick Start 🚀

1. Clone the repository:
```bash
git clone https://github.com/Amarnath-2005-ai/Leaf_disease_prediction.git
cd Leaf_disease_prediction
```

2. Create virtual environment and install dependencies:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. Run the application:
```bash
python app_modern.py
```

The application will automatically:
- Download the required model file from Google Drive
- Show download progress
- Start the web server

Visit `http://127.0.0.1:5000` or `http://localhost:5000` to use the application.

## Project Structure 📁

```
Leaf_disease_prediction/
├── app_modern.py          # Main Flask application
├── models/                # Deep learning models (auto-downloaded)
├── static/               # Static files
│   ├── css/             # Stylesheets
│   │   ├── modern_style.css
│   │   └── bootstrap.min.css
│   └── images/          # Images and icons
│       ├── bg1.jpg
│       └── logo.svg
├── templates/            # HTML templates
│   └── modern_home.html
├── uploadimages/         # Uploaded images storage
└── plant_disease.json    # Disease information database
```

## Features ✨

- Image upload and disease detection
- Detailed disease information and treatment suggestions
- Dark/Light mode
- Responsive design
- Automatic model download
- Progress tracking for downloads

## Tech Stack 🛠️

- Backend: Python, Flask
- Frontend: HTML5, CSS3, Bootstrap 5
- Deep Learning: TensorFlow, Keras
- Additional: Requests, tqdm (for model download)

## Manual Model Download (Optional) 🔧

If you prefer to download the model manually:
1. Download from [Google Drive](https://drive.google.com/uc?export=download&id=1HJBCQTyOrTKgBNJ7gH-H9lB37df_81-7)
2. Place it in the `models` folder as `plant_disease_recog_model_pwp.keras`

---
Made with ❤️ by Amarnath 