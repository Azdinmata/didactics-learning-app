import os
from flask import Flask, render_template, request, jsonify, session, send_from_directory, redirect, url_for
import auth
import ai_assistant
from lesson_data import MODULES

app = Flask(__name__)
app.secret_key = "didactics_hub_premium_secret_key_2026"

# Ensure templates and static directories exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("login_page"))
    return render_template("index.html")

@app.route("/login")
def login_page():
    if "username" in session:
        return redirect(url_for("index"))
    return render_template("login.html")

# --- AUTH APIS ---

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    security_answer = data.get("security_answer", "").strip()
    
    if not username or not password or not security_answer:
        return jsonify({"success": False, "message": "All fields are required."}), 400
        
    success, message = auth.create_user(username, password, security_answer)
    return jsonify({"success": success, "message": message})

@app.route("/api/auth/login", methods=["POST"])
def login_api():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required."}), 400
        
    success, message, user_data = auth.verify_login(username, password)
    if success:
        session["username"] = username
        return jsonify({
            "success": True,
            "message": message,
            "user": {
                "username": username,
                "unlocked_index": user_data["unlocked_index"],
                "quiz_scores": user_data["quiz_scores"]
            }
        })
    return jsonify({"success": False, "message": message}), 401

@app.route("/api/auth/reset", methods=["POST"])
def reset_api():
    data = request.json or {}
    username = data.get("username", "").strip()
    security_answer = data.get("security_answer", "").strip()
    new_password = data.get("new_password", "").strip()
    
    if not username or not security_answer or not new_password:
        return jsonify({"success": False, "message": "All fields are required."}), 400
        
    success, message = auth.reset_password(username, security_answer, new_password)
    return jsonify({"success": success, "message": message})

@app.route("/api/auth/logout", methods=["GET", "POST"])
def logout():
    session.pop("username", None)
    if request.method == "POST":
        return jsonify({"success": True, "message": "Logged out successfully."})
    return redirect(url_for("login_page"))

# --- DATA APIS ---

@app.route("/api/user", methods=["GET"])
def get_user_data():
    if "username" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    username = session["username"]
    # Quick login verification to get latest JSON profile
    users = auth._load_users()
    user_data = users.get(username, {})
    
    # Format quiz scores back to numbers for frontend easy handling
    scores = {int(k): v for k, v in user_data.get("quiz_scores", {}).items()}
    
    return jsonify({
        "success": True,
        "user": {
            "username": username,
            "unlocked_index": user_data.get("unlocked_index", 0),
            "quiz_scores": scores
        }
    })

@app.route("/api/modules", methods=["GET"])
def get_modules():
    if "username" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    # Send custom light-weight course modules outline to frontend (quizzes and metadata)
    outline = []
    for idx, mod in enumerate(MODULES):
        outline.append({
            "index": idx,
            "title": mod["title"],
            "description": mod["description"],
            "quiz": mod["quiz"]  # We keep the quiz questions here for frontend checking
        })
    return jsonify({"success": True, "modules": outline})

@app.route("/api/progress", methods=["POST"])
def update_progress():
    if "username" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    username = session["username"]
    data = request.json or {}
    unlocked_index = data.get("unlocked_index", 0)
    quiz_scores_raw = data.get("quiz_scores", {})
    
    # Cast keys to integers
    quiz_scores = {}
    for k, v in quiz_scores_raw.items():
        try:
            quiz_scores[int(k)] = int(v)
        except ValueError:
            pass
            
    auth.save_user_progress(username, unlocked_index, quiz_scores)
    return jsonify({"success": True, "message": "Progress saved."})

@app.route("/api/chat", methods=["POST"])
def chat_api():
    if "username" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    data = request.json or {}
    chat_history = data.get("history", [])
    module_index = data.get("module_index", -1)
    
    active_mod = None
    if 0 <= module_index < len(MODULES):
        active_mod = MODULES[module_index]
        
    try:
        response = ai_assistant.get_real_response(chat_history, active_mod)
        if not response:
            response = "⚠️ Received empty response. Please try again."
    except Exception as e:
        response = f"⚠️ Error: {str(e)}"
        
    return jsonify({"success": True, "response": response})

# --- FILE SERVING & PDF RENDERING ---

import io
import base64
import pypdfium2 as pdfium

PDF_FILES = [
    "lessons/1) BASIC NOTIONS AND FUNDAMENTALS OF DIDACTICS 1 presentation.pdf",
    "lessons/2) Basic Notions and Fundamentals of Didactics (Foundations of Didacticic).pdf",
    "lessons/3) Learning Theories Behaviorism to TDS.pdf",
    "lessons/4) Methods_and_approaches1_GTM DM ALM SUG SW CLL.pdf",
    "lessons/5)Methods and approaches in language teaching 2 (1).pdf",
    "lessons/6)Didactics-Teaching the Four Skills PPT.pdf",
    "lessons/7) new presentaion for grammar , vocabulary and functions -compressed.pdf",
    "lessons/8) Approach-compressed.pdf",
    "lessons/9) Fundamentals of ELT-EFL.pdf",
    "lessons/10) FUNDAMENTALS of EFL-compressed.pdf"
]

import threading
from flask import send_file

# Global lock to synchronize access to pypdfium2 functions across multi-threaded Flask requests
PDF_LOCK = threading.Lock()

PAGE_IMAGE_CACHE = {}

@app.route("/api/pdf-info/<int:module_idx>")
def get_pdf_info_api(module_idx):
    if "username" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    if module_idx < 0 or module_idx >= len(PDF_FILES):
        return jsonify({"success": False, "message": "Module not found"}), 404
        
    pdf_path = PDF_FILES[module_idx]
    if not os.path.exists(pdf_path):
        return jsonify({"success": False, "message": "PDF file not found"}), 404
        
    try:
        with PDF_LOCK:
            with pdfium.PdfDocument(pdf_path) as doc:
                num_pages = len(doc)
                
        return jsonify({
            "success": True,
            "num_pages": num_pages
        })
    except Exception as e:
        print(f"Error loading PDF info {pdf_path}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/pdf-page-img/<int:module_idx>/<int:page_idx>")
def get_pdf_page_image_api(module_idx, page_idx):
    if "username" not in session:
        return "Unauthorized", 401
        
    cache_key = (module_idx, page_idx)
    if cache_key in PAGE_IMAGE_CACHE:
        return send_file(io.BytesIO(PAGE_IMAGE_CACHE[cache_key]), mimetype="image/jpeg")
        
    if module_idx < 0 or module_idx >= len(PDF_FILES):
        return "Module not found", 404
        
    pdf_path = PDF_FILES[module_idx]
    if not os.path.exists(pdf_path):
        return "PDF file not found", 404
        
    try:
        with PDF_LOCK:
            with pdfium.PdfDocument(pdf_path) as doc:
                if page_idx < 0 or page_idx >= len(doc):
                    return "Page not found", 404
                    
                page = doc.get_page(page_idx)
                # Scale to 2.0 matches standard HD screens razor-sharp
                pil_image = page.render(scale=2).to_pil()
                
                buffer = io.BytesIO()
                pil_image.save(buffer, format="JPEG", quality=80) # 80% quality for lightning-fast transfer
                img_bytes = buffer.getvalue()
                
                PAGE_IMAGE_CACHE[cache_key] = img_bytes
    except Exception as e:
        print(f"Error rendering page {page_idx} of module {module_idx}: {e}")
        return "Error rendering page", 500
        
    return send_file(io.BytesIO(img_bytes), mimetype="image/jpeg")

@app.route("/lessons/<path:filename>")
def serve_lesson_pdf(filename):
    if "username" not in session:
        return "Unauthorized", 401
    return send_from_directory("lessons", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
