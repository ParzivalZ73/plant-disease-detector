from flask import Flask, request, jsonify, render_template
import tensorflow as tf
import numpy as np
import json
import os
from PIL import Image
import io

app = Flask(__name__)

# Load model and class names
MODEL_PATH = os.environ.get("MODEL_PATH", "model/plant_model.h5")
CLASSES_PATH = os.environ.get("CLASSES_PATH", "model/classes.json")

print("Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)
with open(CLASSES_PATH) as f:
    class_names = json.load(f)
print(f"Model loaded. {len(class_names)} classes.")

IMG_SIZE = 224

def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((IMG_SIZE, IMG_SIZE))
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    image_bytes = file.read()
    img_array = preprocess_image(image_bytes)

    predictions = model.predict(img_array)
    pred_idx = int(np.argmax(predictions[0]))
    confidence = float(np.max(predictions[0]))
    label = class_names[pred_idx]

    # Top 3 predictions
    top3_idx = np.argsort(predictions[0])[::-1][:3]
    top3 = [
        {"class": class_names[i], "confidence": float(predictions[0][i])}
        for i in top3_idx
    ]

    return jsonify({
        "prediction": label,
        "confidence": round(confidence * 100, 2),
        "top3": top3
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
