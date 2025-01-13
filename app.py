from flask import Flask, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import GlobalAveragePooling2D
import numpy as np
from tensorflow.keras.applications.resnet50 import preprocess_input

# Initialize Flask app
app = Flask(__name__)

# Configure upload folder and allowed extensions
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Load the saved model
model_path = 'static/model/fish_disease_classifier.h5'
loaded_model = load_model(model_path)
print(f"Model loaded successfully from {model_path}")

# Define class labels
class_labels = [
    "Bacterial diseases - Aeromoniasis",
    "Bacterial gill disease",
    "Bacterial Red diseases",
    "EUS",
    "Fungal diseases Saprolegniasis",
    "Healthy Fish",
    "Parasitic diseases",
    "Viral diseases"
]

# Load ResNet50 for feature extraction
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def preprocess_image(image_path):
    img = tf.keras.utils.load_img(image_path, target_size=(224, 224))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array

def predict_disease(image_path, model):
    preprocessed_img = preprocess_image(image_path)
    features = base_model.predict(preprocessed_img)
    pooled_features = GlobalAveragePooling2D()(features)
    predictions = model.predict(pooled_features)
    predicted_class_idx = np.argmax(predictions)
    predicted_class_label = class_labels[predicted_class_idx]
    confidence = predictions[0][predicted_class_idx]
    return predicted_class_label, confidence

@app.errorhandler(500)
def handle_500_error(e):
    return jsonify({"error": "Server encountered an issue"}), 5000


  

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/endpoint')
def my_endpoint():
    data = {"key": "value"}
    return jsonify(data)  # Always return JSON for APIs

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        print("No 'file' key in request.files")
        return jsonify({'error': 'No file uploaded'})

    file = request.files['file']

    if not file:
        print("File is empty")
        return jsonify({'error': 'No file uploaded'})

    if not allowed_file(file.filename):
        print(f"Invalid file type: {file.filename}")
        return jsonify({'error': 'Invalid file type'})

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        # Get prediction
        predicted_label, confidence = predict_disease(filepath, loaded_model)
        
        # Ensure prediction was successful
        if not predicted_label or not confidence:
            return jsonify({'error': 'Prediction failed, please check the model and image.'})
        
        # Pass the result to the frontend (display.html)
        print(f"Predicted Label: {predicted_label}, Confidence: {confidence}")
        return render_template('display.html', 
                               label=predicted_label, 
                               confidence=confidence, 
                               image_path=filepath)
    
    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({'error': 'An error occurred during prediction.'})
    
   
    
    

if __name__ == '__main__':
    app.run(debug=True)
