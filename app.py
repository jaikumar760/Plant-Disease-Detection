from flask import Flask, jsonify, request
from PIL import Image
import base64
import io

from python_scripts import predict

app = Flask(__name__)


def render_page(result=None, error=None, filename=None, image_url=None, top_preds=None, pred_time=None):
    top_preds = top_preds or []
    if result and top_preds:
        pred_title = result["label"]
        pred_conf = result.get("confidence", "")
        try:
            conf_value = float(pred_conf.replace("%", ""))
        except Exception:
            conf_value = None
        if conf_value is None:
            conf_class = "conf-low"
        elif conf_value >= 80:
            conf_class = "conf-high"
        elif conf_value >= 50:
            conf_class = "conf-mid"
        else:
            conf_class = "conf-low"
        pred_items = "".join(
            [
                f"""
                <div class="pred-item">
                    <div class="pred-row">
                        <div class="pred-label">{label}</div>
                        <div class="pred-pct">{prob * 100:.0f}%</div>
                    </div>
                    <div class="pred-track"><span style="width:{prob * 100:.2f}%"></span></div>
                </div>
                """
                for label, prob in top_preds
            ]
        )
    else:
        pred_title = ""
        pred_conf = ""
        pred_items = """
            <div class="pred-empty">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M4 5h10"></path>
                    <path d="M4 12h16"></path>
                    <path d="M4 19h12"></path>
                </svg>
            </div>
        """

    dropzone_content = (
        f'<img src="{image_url}" alt="Uploaded Image">'
        if image_url
        else """
        <div class="dz-label">
            <div class="dz-icon">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M12 16V7"></path>
                    <path d="M8.5 10.5L12 7l3.5 3.5"></path>
                    <rect x="4" y="16.5" width="16" height="3" rx="1.5"></rect>
                </svg>
            </div>
            <div><strong>Drop Image Here</strong></div>
            <div>- or -</div>
            <div>Click to Upload</div>
        </div>
        """
    )

    return f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Plant Doc</title>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg: #0b0f17;
                --panel: #1b2433;
                --panel-2: #222c3b;
                --text: #e5e7eb;
                --muted: #94a3b8;
                --accent: #f97316;
                --accent-2: #22d3ee;
                --border: #2a3648;
                --soft: #2f394a;
            }}
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                font-family: "Space Grotesk", system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
                color: var(--text);
                background: radial-gradient(1200px 600px at 10% 10%, #0d1a2b 0%, transparent 60%),
                            radial-gradient(900px 500px at 90% 20%, #101827 0%, transparent 60%),
                            var(--bg);
                min-height: 100vh;
            }}
            .wrap {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 40px 24px 64px;
            }}
            header {{
                display: grid;
                gap: 10px;
                margin-bottom: 22px;
            }}
            h1 {{
                font-size: 28px;
                margin: 0;
                letter-spacing: 0.2px;
            }}
            .sub {{
                color: var(--muted);
                font-size: 14px;
            }}
            .grid {{
                display: grid;
                grid-template-columns: 1.05fr 0.95fr;
                gap: 18px;
                align-items: start;
            }}
            .col {{
                display: flex;
                flex-direction: column;
                gap: 16px;
            }}
            @media (max-width: 800px) {{
                .grid {{ grid-template-columns: 1fr; }}
            }}
            .card {{
                background: linear-gradient(180deg, rgba(27, 36, 51, 0.96) 0%, rgba(27, 36, 51, 0.88) 100%);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 14px;
                box-shadow: 0 10px 26px rgba(0, 0, 0, 0.3);
                height: fit-content;
            }}
            .upload {{
                border: 1px solid #273244;
                border-radius: 12px;
                padding: 0;
                background: rgba(18, 25, 37, 0.8);
                overflow: hidden;
            }}
            .upload-top {{
                height: 36px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 12px;
                border-bottom: 1px solid #2b3648;
                background: rgba(26, 35, 49, 0.9);
                color: #dbe2ef;
                font-size: 12px;
            }}
            .upload-top .tag {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 4px 8px;
                border-radius: 6px;
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid #334155;
                color: #e2e8f0;
                font-weight: 600;
                text-transform: lowercase;
            }}
            .upload-top .close {{
                width: 22px;
                height: 22px;
                border-radius: 6px;
                display: grid;
                place-items: center;
                border: 1px solid #334155;
                color: #cbd5f5;
                background: rgba(15, 23, 42, 0.6);
                cursor: pointer;
                padding: 0;
                margin: 0;
                font-size: 14px;
                line-height: 1;
                font: inherit;
                appearance: none;
            }}
            .row {{
                display: flex;
                gap: 12px;
                align-items: center;
                flex-wrap: wrap;
            }}
            .dropzone {{
                min-height: 220px;
                display: grid;
                place-items: center;
                color: var(--muted);
                border-bottom: 1px dashed #394458;
                background: rgba(20, 28, 41, 0.95);
                position: relative;
                cursor: pointer;
            }}
            .dropzone img {{
                max-width: 100%;
                max-height: 260px;
                display: block;
                object-fit: cover;
            }}
            .dz-label {{
                text-align: center;
                display: grid;
                gap: 8px;
                font-size: 14px;
            }}
            .dz-label strong {{
                color: #e2e8f0;
                font-size: 16px;
            }}
            .dz-icon {{
                width: 36px;
                height: 36px;
                border-radius: 999px;
                display: grid;
                place-items: center;
                margin: 0 auto;
                border: 1px solid #394458;
                color: #cbd5f5;
            }}
            .title-icon {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 22px;
                height: 22px;
            }}
            .panel-icon {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 16px;
                height: 16px;
                color: #cbd5f5;
            }}
            input[type="file"] {{
                background: #121a26;
                color: var(--text);
                border: 1px solid #2a3648;
                padding: 10px;
                border-radius: 10px;
            }}
            button {{
                background: linear-gradient(90deg, var(--accent), #f97316);
                border: none;
                color: #1b1f24;
                font-weight: 700;
                padding: 10px 22px;
                border-radius: 8px;
                cursor: pointer;
                transition: transform 120ms ease, filter 120ms ease;
            }}
            button:hover {{
                transform: translateY(-1px);
                filter: brightness(1.05);
            }}
            button[disabled] {{
                opacity: 0.7;
                cursor: not-allowed;
            }}
            .btn-ghost {{
                background: #3a4352;
                color: #f1f5f9;
            }}
            .upload-actions {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
                padding: 12px;
                background: rgba(21, 29, 42, 0.9);
                border-top: 1px solid #2b3648;
            }}
            .upload-actions button {{
                width: 100%;
            }}
            .upload-toolbar {{
                display: flex;
                justify-content: center;
                gap: 14px;
                padding: 10px 0;
                border-top: 1px solid #2b3648;
                background: rgba(21, 29, 42, 0.9);
            }}
            .tool {{
                width: 26px;
                height: 26px;
                border-radius: 8px;
                display: grid;
                place-items: center;
                color: #cbd5f5;
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid #334155;
            }}
            .tool.active {{
                color: #fb923c;
                border-color: #f59e0b;
            }}
            .loading {{
                position: relative;
                pointer-events: none;
            }}
            .loading::after {{
                content: "Predicting...";
                position: absolute;
                inset: 0;
                display: grid;
                place-items: center;
                background: rgba(8, 12, 18, 0.55);
                color: #e2e8f0;
                font-weight: 600;
                letter-spacing: 0.3px;
            }}
            .panel-title {{
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 13px;
                color: #e2e8f0;
                margin-bottom: 10px;
                padding: 4px 8px;
                border-radius: 6px;
                border: 1px solid #334155;
                background: rgba(15, 23, 42, 0.6);
                width: fit-content;
            }}
            .pred-title {{
                text-align: center;
                font-size: 20px;
                font-weight: 700;
                letter-spacing: 0.2px;
                margin: 8px 0 12px;
            }}
            .pred-sub {{
                text-align: center;
                font-size: 12px;
                color: #94a3b8;
                margin-top: -6px;
                margin-bottom: 10px;
                letter-spacing: 0.4px;
                text-transform: uppercase;
            }}
            .conf-badge {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 6px 10px;
                border-radius: 999px;
                border: 1px solid transparent;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.4px;
                text-transform: uppercase;
            }}
            .conf-high {{
                color: #86efac;
                border-color: rgba(34, 197, 94, 0.45);
                background: rgba(34, 197, 94, 0.12);
            }}
            .conf-mid {{
                color: #fde68a;
                border-color: rgba(234, 179, 8, 0.45);
                background: rgba(234, 179, 8, 0.12);
            }}
            .conf-low {{
                color: #fecaca;
                border-color: rgba(239, 68, 68, 0.45);
                background: rgba(239, 68, 68, 0.12);
            }}
            .pred-list {{
                display: grid;
                gap: 10px;
            }}
            .pred-row {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 10px;
                font-size: 13px;
                color: #e2e8f0;
            }}
            .pred-label {{
                font-weight: 500;
            }}
            .pred-pct {{
                color: #e2e8f0;
                font-weight: 600;
                min-width: 36px;
                text-align: right;
            }}
            .pred-empty {{
                height: 60px;
                display: grid;
                place-items: center;
                color: #95a4b8;
                background: rgba(18, 25, 37, 0.5);
                border: 1px solid #2b3648;
                border-radius: 10px;
            }}
            .pred-item {{
                display: grid;
                gap: 6px;
                font-size: 13px;
                padding-bottom: 8px;
                border-bottom: 1px dashed #2e3a4c;
            }}
            .pred-item:last-child {{
                border-bottom: none;
                padding-bottom: 0;
            }}
            .pred-track {{
                height: 3px;
                border-radius: 999px;
                background-image: repeating-linear-gradient(
                    to right,
                    rgba(148, 163, 184, 0.35),
                    rgba(148, 163, 184, 0.35) 3px,
                    transparent 3px,
                    transparent 6px
                );
                position: relative;
                overflow: hidden;
                margin-top: 4px;
            }}
            .pred-track span {{
                position: absolute;
                inset: 0;
                width: 0%;
                background: linear-gradient(90deg, #f59e0b, #f97316);
            }}
            .time-box {{
                margin-top: 8px;
                padding: 12px;
                border-radius: 10px;
                border: 1px solid var(--border);
                background: rgba(20, 27, 39, 0.8);
                display: grid;
                gap: 8px;
            }}
            .time-input {{
                width: 100%;
                padding: 10px 12px;
                border-radius: 8px;
                border: 1px solid #2a3648;
                background: #1b2433;
                color: #e2e8f0;
            }}
            .examples {{
                margin-top: 16px;
                display: grid;
                gap: 10px;
            }}
            .examples-row {{
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }}
            .ex-thumb {{
                width: 64px;
                height: 64px;
                border-radius: 8px;
                overflow: hidden;
                border: 1px solid #2a3648;
                background: #111827;
            }}
            .ex-thumb img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            .k {{
                color: var(--muted);
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1.2px;
            }}
            .v {{
                font-size: 18px;
                font-weight: 700;
                margin-top: 4px;
            }}
            .muted {{ color: var(--muted); }}
            .result {{
                margin-top: 12px;
                padding: 12px;
                border-radius: 12px;
                border: 1px solid #7f1d1d;
                background: rgba(127, 29, 29, 0.2);
            }}
        </style>
    </head>
    <body>
        <div class="wrap">
            <header>
                <h1>
                    Plant Doc
                    <span class="title-icon" aria-hidden="true">
                        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#22c55e" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M4 14c6.5 1 10.5-3 12-9 3 2 4.5 6 1 10-2.2 2.5-6.5 3.7-10.8 2.8C4.6 17.4 4 16 4 14z"></path>
                            <path d="M8 12c2.8-1.6 5.2-4.3 6.5-7.2"></path>
                        </svg>
                    </span>
                </h1>
                <div class="sub">An EfficientNetB0 feature extractor computer vision model to classify the diseases in plants</div>
            </header>
            <div class="grid">
                <div class="col">
                    <div class="card">
                        <div class="upload">
                            <div class="upload-top">
                                <span class="tag">
                                    <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                                        <rect x="4" y="4" width="16" height="16" rx="2"></rect>
                                        <path d="M8 16l3-3 3 3 4-5"></path>
                                    </svg>
                                    img
                                </span>
                                <button id="closeBtn" class="close" type="button" aria-label="Clear image">×</button>
                            </div>
                            <form action="/predict" method="post" enctype="multipart/form-data">
                                <input id="imageInput" type="file" name="image" accept="image/*" required hidden>
                                <div class="dropzone" id="dropzone">{dropzone_content}</div>
                                <div class="upload-toolbar">
                                    <span class="tool active">
                                        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                                            <path d="M12 5v14"></path>
                                            <path d="M5 12h14"></path>
                                        </svg>
                                    </span>
                                    <span class="tool">
                                        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                                            <circle cx="12" cy="12" r="3"></circle>
                                            <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V22a2 2 0 1 1-4 0v-.2a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H2a2 2 0 1 1 0-4h.2a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H8a1.7 1.7 0 0 0 1-1.5V2a2 2 0 1 1 4 0v.2a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V8c0 .7.4 1.3 1 1.5.2.1.4.1.6.1H22a2 2 0 1 1 0 4h-.2a1.7 1.7 0 0 0-1.5 1z"></path>
                                        </svg>
                                    </span>
                                    <span class="tool">
                                        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                                            <path d="M12 20h9"></path>
                                            <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"></path>
                                        </svg>
                                    </span>
                                </div>
                                <div class="upload-actions">
                                    <button id="clearBtn" class="btn-ghost" type="button">Clear</button>
                                    <button id="submitBtn" type="submit">Submit</button>
                                </div>
                            </form>
                        </div>
                        {f"""
                        <div class="result">
                            <div class="k">Error</div>
                            <div class="v">{error}</div>
                        </div>
                        """ if error else ""}
                    </div>
                    <div class="examples">
                    <div class="panel-title">
                            <span class="panel-icon" aria-hidden="true">
                                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                                    <rect x="3.5" y="4.5" width="17" height="15" rx="2"></rect>
                                    <path d="M7 14l3-3 3 3 4-5"></path>
                                </svg>
                            </span>
                            Examples
                        </div>
                        <div class="examples-row">
                            <div class="ex-thumb"><img alt="example 1" src="/static/examples/example-1.jpg"></div>
                            <div class="ex-thumb"><img alt="example 2" src="/static/examples/example-2.jpg"></div>
                            <div class="ex-thumb"><img alt="example 3" src="/static/examples/example-3.jpg"></div>
                        </div>
                        <div class="muted">Created [Today]</div>
                    </div>
                </div>
                <div class="col">
                    <div class="card">
                        <div class="panel-title">
                            <span class="panel-icon" aria-hidden="true">
                                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M4 5h10"></path>
                                    <path d="M4 12h16"></path>
                                    <path d="M4 19h12"></path>
                                </svg>
                            </span>
                            Predictions
                    </div>
                    <div class="pred-title">{pred_title}</div>
                    {f'<div class="pred-sub"><span class="conf-badge {conf_class}">Confidence {pred_conf}</span></div>' if pred_conf else ''}
                    <div class="pred-list">{pred_items}</div>
                    </div>
                    <div class="card">
                        <div class="k">Prediction time (s)</div>
                        <div class="time-box">
                            <input class="time-input" value="{pred_time or '0'}" readonly>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script>
            const dropzone = document.getElementById("dropzone");
            const input = document.getElementById("imageInput");
            const clearBtn = document.getElementById("clearBtn");
            const closeBtn = document.getElementById("closeBtn");
            const submitBtn = document.getElementById("submitBtn");
            const form = document.querySelector("form");
            if (dropzone && input) {{
                dropzone.addEventListener("click", () => input.click());
                dropzone.addEventListener("dragover", (e) => {{
                    e.preventDefault();
                    dropzone.style.borderColor = "#f97316";
                }});
                dropzone.addEventListener("dragleave", () => {{
                    dropzone.style.borderColor = "#2a3648";
                }});
                dropzone.addEventListener("drop", (e) => {{
                    e.preventDefault();
                    dropzone.style.borderColor = "#2a3648";
                    const file = e.dataTransfer.files && e.dataTransfer.files[0];
                    if (!file) return;
                    input.files = e.dataTransfer.files;
                    const url = URL.createObjectURL(file);
                    dropzone.innerHTML = `<img src="${{url}}" alt="Preview">`;
                }});
            }}
            if (input && dropzone) {{
                input.addEventListener("change", () => {{
                    const file = input.files && input.files[0];
                    if (!file) {{
                        dropzone.innerHTML = `<div class="dz-label">
                            <div class="dz-icon">
                                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                    <path d="M12 16V7"></path>
                                    <path d="M8.5 10.5L12 7l3.5 3.5"></path>
                                    <rect x="4" y="16.5" width="16" height="3" rx="1.5"></rect>
                                </svg>
                            </div>
                            <div><strong>Drop Image Here</strong></div>
                            <div>- or -</div>
                            <div>Click to Upload</div>
                        </div>`;
                        return;
                    }}
                    const url = URL.createObjectURL(file);
                    dropzone.innerHTML = `<img src="${{url}}" alt="Preview">`;
                }});
            }}
            const resetDropzone = () => {{
                if (!input || !dropzone) return;
                input.value = "";
                dropzone.innerHTML = `<div class="dz-label">
                        <div class="dz-icon">
                            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                <path d="M12 16V7"></path>
                                <path d="M8.5 10.5L12 7l3.5 3.5"></path>
                                <rect x="4" y="16.5" width="16" height="3" rx="1.5"></rect>
                            </svg>
                        </div>
                        <div><strong>Drop Image Here</strong></div>
                        <div>- or -</div>
                        <div>Click to Upload</div>
                    </div>`;
                window.location.href = "/";
            }};
            if (clearBtn) {{
                clearBtn.addEventListener("click", resetDropzone);
            }}
            if (closeBtn) {{
                closeBtn.addEventListener("click", resetDropzone);
            }}
            if (form && submitBtn) {{
                form.addEventListener("submit", () => {{
                    submitBtn.setAttribute("disabled", "disabled");
                    if (dropzone) {{
                        dropzone.classList.add("loading");
                    }}
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
        sorted_preds = sorted(prediction.items(), key=lambda x: x[1], reverse=True)[:5]
        label, confidence = sorted_preds[0]

        result_payload = {
            "label": label,
            "confidence": f"{confidence * 100:.2f}%",
            "time": f"{pred_time}s"
        }

        mime = file.mimetype or "image/png"
        b64 = base64.b64encode(file_bytes).decode("ascii")
        image_url = f"data:{mime};base64,{b64}"

        if request.args.get("format") == "json" or request.accept_mimetypes.best == "application/json":
            return jsonify([prediction, pred_time]), 200

        return render_page(
            result=result_payload,
            filename=file.filename,
            image_url=image_url,
            top_preds=sorted_preds,
            pred_time=f"{pred_time:.5f}"
        ), 200
    except Exception as e:
        return render_page(error=str(e)), 500


if __name__ == "__main__":
    # Hugging Face Spaces expects the app to listen on 0.0.0.0:7860
    port = int(__import__("os").environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port, debug=False)
