from flask import Flask, render_template, request, redirect, url_for, session
import json, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "your_secret_key"

DATA_FILE = "data.json"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Load driver data
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"drivers": []}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)


# Save driver data
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        data = load_data()
        for driver in data["drivers"]:
            if driver["username"] == username and driver["password"] == password:
                session["username"] = username
                return redirect(url_for("profile"))

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Login details
        username = request.form["username"]
        password = request.form["password"]

        # Profile details
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

        # Save to data.json
        data = load_data()
        data["drivers"].append(driver_data)
        save_data(data)

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login"))

    data = load_data()
    for driver in data["drivers"]:
        if driver["username"] == session["username"]:
            return render_template("profile.html", driver=driver)

    return redirect(url_for("login"))


@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "username" not in session:
        return redirect(url_for("login"))

    data = load_data()
    for driver in data["drivers"]:
        if driver["username"] == session["username"]:
            if request.method == "POST":
                # Update fields
                driver["name"] = request.form.get("name", "")
                driver["age"] = request.form.get("age", "")
                driver["weight"] = request.form.get("weight", "")
                driver["medical_conditions"] = request.form.get("medical_conditions", "")
                driver["heart_rate_range"] = request.form.get("heart_rate_range", "")
                driver["spo2"] = request.form.get("spo2", "")
                driver["emergency_contact"] = request.form.get("emergency_contact", "")
                driver["medications"] = request.form.get("medications", "")
                driver["blood_glucose"] = request.form.get("blood_glucose", "")
                driver["blood_group"] = request.form.get("blood_group", "")
                driver["license_number"] = request.form.get("license_number", "")

                # Handle photo update
                if "photo" in request.files:
                    file = request.files["photo"]
                    if file.filename != "":
                        filename = secure_filename(file.filename)
                        photo_path = os.path.join(UPLOAD_FOLDER, filename)
                        file.save(photo_path)
                        driver["photo"] = photo_path

                save_data(data)
                return redirect(url_for("profile"))

            return render_template("edit_profile.html", driver=driver)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
