from flask import Flask, jsonify, request
from PIL import Image
import base64
import io

from python_scripts import predict

app = Flask(__name__)

def render_page(result=None, error=None, filename=None, raw_json=None, image_url=None):
    return f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Plant Disease Detection</title>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg: #0f172a;
                --panel: #111827;
                --text: #e5e7eb;
                --muted: #9ca3af;
                --accent: #22c55e;
                --accent-2: #38bdf8;
                --accent-3: #f59e0b;
                --border: #1f2937;
            }}
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                font-family: "Space Grotesk", system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
                color: var(--text);
                background: radial-gradient(1200px 600px at 10% 10%, #0b3a2e 0%, transparent 60%),
                            radial-gradient(900px 500px at 90% 20%, #0b2a4a 0%, transparent 60%),
                            var(--bg);
                min-height: 100vh;
            }}
            .wrap {{
                max-width: 980px;
                margin: 0 auto;
                padding: 48px 20px 64px;
            }}
            header {{
                display: grid;
                gap: 8px;
                margin-bottom: 24px;
            }}
            h1 {{
                font-size: 36px;
                margin: 0;
                letter-spacing: 0.4px;
            }}
            .sub {{
                color: var(--muted);
                font-size: 16px;
            }}
            .grid {{
                display: grid;
                grid-template-columns: 1.1fr 0.9fr;
                gap: 20px;
                align-items: start;
            }}
            @media (max-width: 800px) {{
                .grid {{ grid-template-columns: 1fr; }}
            }}
            .hero {{
                display: flex;
                align-items: center;
                gap: 12px;
                flex-wrap: wrap;
            }}
            .card {{
                background: linear-gradient(180deg, rgba(17, 24, 39, 0.9) 0%, rgba(17, 24, 39, 0.7) 100%);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
                height: fit-content;
            }}
            .upload {{
                border: 1px dashed #334155;
                border-radius: 12px;
                padding: 18px;
                background: rgba(15, 23, 42, 0.6);
            }}
            .preview {{
                margin-top: 14px;
                border: 1px solid #223047;
                border-radius: 12px;
                overflow: hidden;
                background: rgba(2, 6, 23, 0.6);
                min-height: 180px;
                display: grid;
                place-items: center;
            }}
            .preview img {{
                max-width: 100%;
                height: auto;
                display: block;
            }}
            .row {{
                display: flex;
                gap: 12px;
                align-items: center;
                flex-wrap: wrap;
            }}
            input[type="file"] {{
                background: #0b1220;
                color: var(--text);
                border: 1px solid #1f2a44;
                padding: 10px;
                border-radius: 10px;
            }}
            button {{
                background: linear-gradient(90deg, var(--accent), #16a34a);
                border: none;
                color: #0b1220;
                font-weight: 700;
                padding: 10px 18px;
                border-radius: 10px;
                cursor: pointer;
                transition: transform 120ms ease, filter 120ms ease;
            }}
            button:hover {{
                transform: translateY(-1px);
                filter: brightness(1.05);
            }}
            .badge {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 6px 10px;
                border-radius: 999px;
                background: rgba(34, 197, 94, 0.12);
                color: #86efac;
                font-size: 12px;
                border: 1px solid rgba(34, 197, 94, 0.35);
            }}
            .chip {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 6px 10px;
                border-radius: 999px;
                background: rgba(56, 189, 248, 0.12);
                color: #7dd3fc;
                font-size: 12px;
                border: 1px solid rgba(56, 189, 248, 0.35);
            }}
            .result {{
                margin-top: 12px;
                padding: 12px;
                border-radius: 12px;
                border: 1px solid #223047;
                background: rgba(2, 6, 23, 0.6);
            }}
            .k {{
                color: var(--muted);
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1.2px;
            }}
            .v {{
                font-size: 20px;
                font-weight: 700;
                margin-top: 4px;
            }}
            .muted {{ color: var(--muted); }}
            .metrics {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
            }}
            @media (max-width: 520px) {{
                .metrics {{ grid-template-columns: 1fr; }}
            }}
            .metric {{
                padding: 10px;
                border-radius: 12px;
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid #223047;
            }}
            .fade-in {{
                animation: fade 400ms ease-out;
            }}
            @keyframes fade {{
                from {{ opacity: 0; transform: translateY(4px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
        </style>
    </head>
    <body>
        <div class="wrap">
            <header>
                <div class="hero">
                    <div class="badge">EfficientNet-B0 * 38 Classes</div>
                    <div class="chip">CPU Inference</div>
                </div>
                <h1>Plant Disease Detection</h1>
                <div class="sub">Upload a leaf image and get a fast prediction with confidence.</div>
            </header>
            <div class="grid">
                <div class="card">
                    <div class="upload">
                        <form action="/predict" method="post" enctype="multipart/form-data">
                            <div class="row">
                                <input id="imageInput" type="file" name="image" accept="image/*" required>
                                <button type="submit">Predict</button>
                            </div>
                            <div class="muted" style="margin-top:10px;">Tip: Use a clear, well-lit leaf image (JPG/PNG).</div>
                        </form>
                        <div class="preview" id="previewBox">
                            {f'<img src="{image_url}" alt="Uploaded Image">' if image_url else '<div class="muted">Image preview will appear here.</div>'}
                        </div>
                    </div>
                    {f'''
                    <div class="result fade-in">
                        <div class="k">Uploaded File</div>
                        <div class="v">{filename or "--"}</div>
                        <div style="height:12px"></div>
                        <div class="k">Prediction</div>
                        <div class="v">{result["label"]}</div>
                        <div style="height:12px"></div>
                        <div class="metrics">
                            <div class="metric">
                                <div class="k">Confidence</div>
                                <div class="v">{result["confidence"]}</div>
                            </div>
                            <div class="metric">
                                <div class="k">Inference Time</div>
                                <div class="v">{result["time"]}</div>
                            </div>
                        </div>
                    </div>
                    ''' if result else ""}
                    {f'''
                    <div class="result" style="border-color:#1f3b5b;">
                        <div class="k">Raw JSON</div>
                        <pre style="white-space:pre-wrap;margin:8px 0 0;color:#cbd5e1;">{raw_json}</pre>
                    </div>
                    ''' if raw_json else ""}
                    {f'''
                    <div class="result" style="border-color:#7f1d1d; background: rgba(127, 29, 29, 0.2);">
                        <div class="k">Error</div>
                        <div class="v">{error}</div>
                    </div>
                    ''' if error else ""}
                </div>
                <div class="card">
                    <div class="k">Workflow</div>
                    <div class="v">Leaf Image → Model → Result</div>
                    <p class="muted" style="margin-top:10px;">
                        EfficientNet-B0 predicts one of 38 classes (healthy or disease)
                        and returns confidence in milliseconds.
                    </p>
                    <div style="height:12px"></div>
                    <div class="k">API</div>
                    <p class="muted" style="margin-top:10px;">
                        POST <code>/predict</code> with form-data field <code>image</code>.
                    </p>
                </div>
            </div>
        </div>
        <script>
            const input = document.getElementById("imageInput");
            const previewBox = document.getElementById("previewBox");
            if (input && previewBox) {{
                input.addEventListener("change", () => {{
                    const file = input.files && input.files[0];
                    if (!file) {{
                        previewBox.innerHTML = '<div class="muted">Image preview will appear here.</div>';
                        return;
                    }}
                    const url = URL.createObjectURL(file);
                    previewBox.innerHTML = `<img src="${{url}}" alt="Preview">`;
                }});
            }}
        </script>
    </body>
    </html>"""

@app.route("/", methods=["GET"])
def home():
    return render_page()
    

@app.route("/predict", methods=["POST"])
def process_image():
  try:
    if "image" not in request.files:
      return render_page(error="No image file uploaded"), 400

    file = request.files["image"]
    file_bytes = file.read()
    img = Image.open(io.BytesIO(file_bytes))

    prediction, pred_time = predict.predict(img=img)
    label, confidence = next(iter(prediction.items()))

    result_payload = {
        "label": label,
        "confidence": f"{confidence * 100:.2f}%",
        "time": f"{pred_time}s"
    }
    raw_json = f'[{{"{label}": {confidence}}}, {pred_time}]'
    mime = file.mimetype or "image/png"
    b64 = base64.b64encode(file_bytes).decode("ascii")
    image_url = f"data:{mime};base64,{b64}"

    if request.args.get("format") == "json" or request.accept_mimetypes.best == "application/json":
      return jsonify([prediction, pred_time]), 200

    return render_page(result=result_payload, filename=file.filename, raw_json=raw_json, image_url=image_url), 200
  except Exception as e:
    return render_page(error=str(e)), 500







