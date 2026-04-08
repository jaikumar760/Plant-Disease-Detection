# Plant Disease Detection (PyTorch + Flask)

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://jai-1656-plant-disease-detection.hf.space)

Live Demo (App): https://jai-1656-plant-disease-detection.hf.space
Space Page: https://huggingface.co/spaces/Jai-1656/Plant-Disease-Detection

Live Demo: https://huggingface.co/spaces/Jai-1656/Plant-Disease-Detection

Web application for plant leaf disease classification using a trained EfficientNet-B0 model. Upload a JPG/PNG image and receive the predicted class, confidence, and inference time.

## Highlights
- 38 plant disease/healthy classes
- EfficientNet-B0 inference on CPU
- Simple Flask UI and JSON API
- Fast local predictions

## Requirements
- Python 3.10+ (tested on 3.12)
- PyTorch and Torchvision
- Flask

## Project Structure
- `app.py` — Flask routes and UI
- `wsgi.py` — WSGI entrypoint
- `python_scripts/` — model and prediction logic
- `saved_models/` — trained model weights

## Quickstart
```bash
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# macOS/Linux
# source .venv/bin/activate

python -m pip install -r requirements.txt
python wsgi.py
```

Then open `http://127.0.0.1:5000`.

> Note: `numpy<2` is required for the pinned PyTorch build.

## API
`POST /predict`
- Form-data field: `image` (file)
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
- For production, use a proper WSGI server (e.g., gunicorn on Linux).

## License
MIT
