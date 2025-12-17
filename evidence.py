# evidence.py
import os
import json
import datetime
from PIL import ImageGrab


def _ensure_dir(path="evidence"):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def save_evidence(app, filename_prefix="ERROR"):
    """เดิม – บันทึกภาพอย่างเดียว"""
    evidence_dir = _ensure_dir()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{evidence_dir}/{filename_prefix}_{timestamp}.png"

    try:
        if app and app.top_window().exists():
            app.top_window().capture_as_image().save(filename)
        else:
            ImageGrab.grab().save(filename)

        print(f"[!!] Evidence saved: {filename}")
        return filename

    except Exception as e:
        print(f"[!!] Failed to save evidence: {e}")
        return None


def save_evidence_context(app, context: dict):
    """
    ใหม่ – Save ทั้งรูป + JSON context
    context ควรมี key: test_name, step_name, input_params, error_message
    """
    evidence_dir = _ensure_dir()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"{context.get('step_name','step')}_{timestamp}"

    # 1) Save screenshot
    img_path = f"{evidence_dir}/{base}.png"
    try:
        if app and app.top_window().exists():
            app.top_window().capture_as_image().save(img_path)
        else:
            ImageGrab.grab().save(img_path)
    except Exception as e:
        print(f"[!!] Failed to capture screenshot: {e}")

    # 2) Save JSON
    json_path = f"{evidence_dir}/{base}.json"
    context["timestamp"] = timestamp
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(context, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[!!] Failed to save json evidence: {e}")

    print(f"[!!] Evidence saved:\n - {img_path}\n - {json_path}")

    return img_path, json_path