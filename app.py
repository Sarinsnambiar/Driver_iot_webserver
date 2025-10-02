import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, render_template, redirect, url_for, session
import os
from werkzeug.utils import secure_filename

# -------------------- Flask Setup --------------------
app = Flask(__name__)
app.secret_key = "your_secret_key"  # change this to a secure key
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------- Firebase Setup --------------------
cred = credentials.Certificate("serviceAccountKey.json")  # Make sure this file exists
firebase_admin.initialize_app(cred)
db = firestore.client()

# -------------------- Helper Functions --------------------
def load_driver(username):
    """Load a single driver from Firestore"""
    doc = db.collection("drivers").document(username).get()
    if doc.exists:
        return doc.to_dict()
    return None

def save_driver(driver_data):
    """Save driver data to Firestore"""
    db.collection("drivers").document(driver_data["username"]).set(driver_data)

# -------------------- Routes --------------------
@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        driver = load_driver(username)
        if driver and driver["password"] == password:
            session["username"] = username
            return redirect(url_for("profile"))
        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        driver_data = {
            "username": username,
            "password": password,
            "name": request.form.get("name", ""),
            "age": request.form.get("age", ""),
            "weight": request.form.get("weight", ""),
            "medical_conditions": request.form.get("medical_conditions", ""),
            "heart_rate_range": request.form.get("heart_rate_range", ""),
            "spo2": request.form.get("spo2", ""),
            "emergency_contact": request.form.get("emergency_contact", ""),
            "medications": request.form.get("medications", ""),
            "blood_glucose": request.form.get("blood_glucose", ""),
            "blood_group": request.form.get("blood_group", ""),
            "license_number": request.form.get("license_number", ""),
            "photo": ""
        }

        # Handle photo upload
        if "photo" in request.files:
            file = request.files["photo"]
            if file.filename != "":
                filename = secure_filename(file.filename)
                photo_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(photo_path)
                driver_data["photo"] = photo_path

        save_driver(driver_data)
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login"))

    driver = load_driver(session["username"])
    if driver:
        return render_template("profile.html", driver=driver)

    return redirect(url_for("login"))

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "username" not in session:
        return redirect(url_for("login"))

    driver = load_driver(session["username"])
    if not driver:
        return redirect(url_for("login"))

    if request.method == "POST":
        for key in ["name","age","weight","medical_conditions","heart_rate_range",
                    "spo2","emergency_contact","medications","blood_glucose",
                    "blood_group","license_number"]:
            driver[key] = request.form.get(key, "")

        # Handle photo upload
        if "photo" in request.files:
            file = request.files["photo"]
            if file.filename != "":
                filename = secure_filename(file.filename)
                photo_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(photo_path)
                driver["photo"] = photo_path

        save_driver(driver)
        return redirect(url_for("profile"))

    return render_template("edit_profile.html", driver=driver)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

# -------------------- Run App --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
