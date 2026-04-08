from flask import Flask, jsonify, request , send_from_directory
from PIL import Image

from python_scripts import predict

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Image Prediction</title>
    </head>
    <body>
        <h1>Upload Image</h1>
        <form action="/predict" method="post" enctype="multipart/form-data">
            <input type="file" name="image">
            <button type="submit">Predict</button>
        </form>
    </body>
    </html>"""
    

@app.route("/predict", methods=["POST"])
def process_image():
  try:
    # Check if image file is uploaded
    if "image" not in request.files:
      return jsonify({"error": "No image file uploaded"}), 400

    # Open the image file
    img = Image.open(request.files["image"].stream)

    # Call the prediction function
    result = predict.predict(img=img)

    # Return the prediction result
    return jsonify(result), 200
  except Exception as e:
    # Handle any errors during processing
    return jsonify({"error": str(e)}), 500





