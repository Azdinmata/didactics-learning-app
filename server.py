import os
import io
import pypdfium2 as pdfium
from flask import Flask, render_template, request, jsonify, session, send_from_directory, redirect, url_for, send_file
import auth
import ai_assistant
from lesson_data import MODULES

# Local PDF files mapping for offline server-side rendering
PDF_FILES = [
    "1) BASIC NOTIONS AND FUNDAMENTALS OF DIDACTICS 1 presentation.pdf",
    "2) Basic Notions and Fundamentals of Didactics (Foundations of Didacticic).pdf",
    "3) Learning Theories Behaviorism to TDS.pdf",
    "4) Methods_and_approaches1_GTM DM ALM SUG SW CLL.pdf",
    "5)Methods and approaches in language teaching 2 (1).pdf",
    "6)Didactics-Teaching the Four Skills PPT.pdf",
    "7) new presentaion for grammar , vocabulary and functions -compressed.pdf",
    "8) Approach-compressed.pdf",
    "9) Fundamentals of ELT-EFL.pdf",
    "10) FUNDAMENTALS of EFL-compressed.pdf"
]

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "didactics_hub_premium_super_secure_key"

# Ensure lessons directory exists
os.makedirs("lessons", exist_ok=True)

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

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    
    if not username or not password:
        return jsonify({"success": False, "message": "Please enter both username and password."}), 400
        
    success, message, user_data = auth.verify_login(username, password)
    if success and user_data:
        session["username"] = username
        session["unlocked_index"] = user_data.get("unlocked_index", 0)
        session["quiz_scores"] = user_data.get("quiz_scores", {})
        session["is_new_user"] = user_data.get("is_new_user", False)
        return jsonify({
            "success": True,
            "message": "Welcome!" if session["is_new_user"] else "Welcome back!",
            "user": {
                "username": username,
                "unlocked_index": session["unlocked_index"],
                "quiz_scores": session["quiz_scores"],
                "is_new_user": session["is_new_user"]
            }
        })
    return jsonify({"success": False, "message": message}), 401

@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    security_answer = data.get("security_answer", "").strip()
    
    if not username or not password or not security_answer:
        return jsonify({"success": False, "message": "All fields are required."}), 400
        
    success, message = auth.create_user(username, password, security_answer)
    if success:
        return jsonify({"success": True, "message": message})
    return jsonify({"success": False, "message": message}), 400

@app.route("/api/auth/reset_password", methods=["POST"])
def api_reset_password():
    data = request.json or {}
    username = data.get("username", "").strip()
    security_answer = data.get("security_answer", "").strip()
    new_password = data.get("new_password", "")
    
    if not username or not security_answer or not new_password:
        return jsonify({"success": False, "message": "All fields are required."}), 400
        
    success, message = auth.reset_password(username, security_answer, new_password)
    if success:
        return jsonify({"success": True, "message": message})
    return jsonify({"success": False, "message": message}), 400

@app.route("/api/auth/logout", methods=["POST", "GET"])
def api_logout():
    session.clear()
    if request.method == "POST":
        return jsonify({"success": True, "message": "Logged out successfully."})
    return redirect(url_for("login_page"))

@app.route("/api/user", methods=["GET"])
def api_get_user():
    if "username" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    return jsonify({
        "success": True,
        "user": {
            "username": session["username"],
            "unlocked_index": session.get("unlocked_index", 0),
            "quiz_scores": session.get("quiz_scores", {}),
            "is_new_user": session.get("is_new_user", False)
        }
    })

@app.route("/api/progress", methods=["POST"])
def api_save_progress():
    if "username" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    data = request.json or {}
    unlocked_index = data.get("unlocked_index", session.get("unlocked_index", 0))
    quiz_scores = data.get("quiz_scores", session.get("quiz_scores", {}))
    
    # Force format keys to int for python-level handlers and string for serialization
    formatted_scores = {int(k): int(v) for k, v in quiz_scores.items()}
    
    # Save using auth helper
    auth.save_user_progress(session["username"], unlocked_index, formatted_scores)
    
    session["unlocked_index"] = unlocked_index
    session["quiz_scores"] = {str(k): v for k, v in formatted_scores.items()}
    
    return jsonify({
        "success": True,
        "unlocked_index": unlocked_index,
        "quiz_scores": session["quiz_scores"]
    })

@app.route("/api/modules", methods=["GET"])
def api_get_modules():
    if "username" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    # Standardize modules list to return cleanly
    clean_modules = []
    for idx, mod in enumerate(MODULES):
        clean_modules.append({
            "id": idx,
            "title": mod.get("title", f"Module {idx+1}"),
            "description": mod.get("description", ""),
            "structured_lesson": mod.get("structured_lesson", ""),
            "quiz": mod.get("quiz", [])
        })
    return jsonify({"success": True, "modules": clean_modules})

@app.route("/api/chat", methods=["POST"])
def api_chat():
    if "username" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    data = request.json or {}
    messages = data.get("messages", [])
    current_module_index = data.get("current_module_index", -1)
    
    current_mod = None
    if 0 <= current_module_index < len(MODULES):
        current_mod = MODULES[current_module_index]
        
    # Call Socratic tutor get_real_response method
    response = ai_assistant.get_real_response(messages, current_mod)
    return jsonify({"success": True, "response": response})

@app.route("/lessons/<path:filename>")
def serve_lesson_pdf(filename):
    if "username" not in session:
        return redirect(url_for("login_page"))
    return send_from_directory("lessons", filename)

@app.route("/api/slides/<int:module_idx>/meta")
def api_slide_meta(module_idx):
    if "username" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    if not (0 <= module_idx < len(PDF_FILES)):
        return jsonify({"success": False, "message": "Invalid module index"}), 400
        
    pdf_path = os.path.join("lessons", PDF_FILES[module_idx])
    if not os.path.exists(pdf_path):
        return jsonify({"success": False, "message": "PDF file not found"}), 404
        
    try:
        doc = pdfium.PdfDocument(pdf_path)
        return jsonify({"success": True, "num_pages": len(doc)})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/slides/<int:module_idx>/<int:page_num>")
def api_slide_render(module_idx, page_num):
    if "username" not in session:
        return redirect(url_for("login_page"))
    if not (0 <= module_idx < len(PDF_FILES)):
        return "Invalid module index", 400
        
    pdf_path = os.path.join("lessons", PDF_FILES[module_idx])
    if not os.path.exists(pdf_path):
        return "PDF file not found", 404
        
    try:
        doc = pdfium.PdfDocument(pdf_path)
        if not (1 <= page_num <= len(doc)):
            return "Invalid page number", 400
            
        page = doc[page_num - 1]
        # scale=2 gives 144 DPI sharp rendering, scale=3 gives 216 DPI (very high end)
        bitmap = page.render(scale=2.5)
        pil_img = bitmap.to_pil()
        
        img_io = io.BytesIO()
        pil_img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return f"Error rendering page: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)