# Plant Disease Detection (PyTorch + Flask)

A lightweight web app that predicts plant leaf diseases from an uploaded image using a trained EfficientNet-B0 model. The app runs locally with Flask and returns the predicted class with confidence and inference time.

## Demo
- Upload a plant leaf image (JPG/PNG)
- Click **Predict**
- Get predicted class + confidence

## Features
- 38 plant disease/healthy classes
- EfficientNet-B0 inference (CPU)
- Simple Flask UI + JSON API
- Fast local inference

## Tech Stack
- Python 3.10+ (tested on 3.12)
- PyTorch, Torchvision
- Flask

## Project Structure
- `app.py` — Flask routes + UI
- `wsgi.py` — WSGI entrypoint
- `python_scripts/` — model + prediction logic
- `saved_models/` — trained model weights

## Setup
```bash
# Create venv
python -m venv .venv

# Activate venv
# Windows
.\.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

> Note: `numpy<2` is required due to PyTorch compatibility in this build.

## Run Locally
```bash
python wsgi.py
```
Then open: http://127.0.0.1:5000

## API
`POST /predict`
- Form-data: `image` (file)
- Response: JSON with predicted class and confidence

Example response:
```json
[
  {"Blueberry___healthy": 0.5795},
  0.2136
]
```

## Classes
All supported classes are listed in `python_scripts/class_names.txt`.

## Notes
- First run may download EfficientNet weights to `~/.cache/torch/hub`.
- For production, use a proper WSGI server (e.g. gunicorn on Linux).

## License
MIT (add/update if you want a different license)
