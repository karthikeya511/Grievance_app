from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import joblib
import smtplib
from email.mime.text import MIMEText
from bson.objectid import ObjectId

# ==========================================
# Flask App Setup
# ==========================================
app = Flask(__name__)
app.secret_key = "supersecretkey"

# Replace this with your actual MongoDB Atlas URI
app.config["MONGO_URI"] = "mongodb+srv://chidellakarthikeya_db_user:Test3122@cluster0.l4ezk5e.mongodb.net/Grievance_db"
mongo = PyMongo(app)

# ==========================================
# Load Trained AI Model and Vectorizer
# ==========================================
model = joblib.load("model/complaint_classifier.pkl")
vectorizer = joblib.load("model/tfidf_vectorizer.pkl")
label_encoder = joblib.load("model/label_encoder.pkl")

department_emails = {
    "Roads": "ravurigowtham07@gmail.com",
    "Sanitation": "ravurigowtham07@gmail.com",
    "Electricity": "ravurigowtham07@gmail.com",
    "Water": "ravurigowtham07@gmail.com",
    "Health": "ravurigowtham07@gmail.com",
    "Education": "ravurigowtham07@gmail.com",
    "PublicSafety": "ravurigowtham07@gmail.com",
    "Agriculture": "ravurigowtham07@gmail.com",
    "Transport": "ravurigowtham07@gmail.com",
    "Other": "ravurigowtham07@gmail.com"
}

# ==========================================
# Utility Functions
# ==========================================
def predict_category(text):
    X = vectorizer.transform([text])
    pred_id = model.predict(X)[0]
    return label_encoder.inverse_transform([pred_id])[0]

def send_email(to_email,category, subject, body):
    sender = "karthikeya3122@gmail.com"
    password = "tgqs kbtq plvp gcrz"  # use Gmail App Password

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        flash(f"{category} department is notified")
    except Exception as e:
        flash(f"⚠️ Email failed")
        redirect(url_for("dashboard"))

# ==========================================
# Routes
# ==========================================
@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard")) if session["role"] == "user" else redirect(url_for("admin_dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if mongo.db.users.find_one({"email": email}):
            flash("Email already registered.")
            return redirect(url_for("register"))

        mongo.db.users.insert_one({
            "username": username,
            "email": email,
            "password": generate_password_hash(password),
            "role": "user"
        })
        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = mongo.db.users.find_one({"email": email})

        if user and check_password_hash(user["password"], password):
            session["user"] = user["username"]
            session["role"] = user["role"]
            flash(f"Welcome, {user['username']}!")
            return redirect(url_for("dashboard" if user["role"] == "user" else "admin_dashboard"))
        else:
            flash("Invalid email or password.")
    return render_template("login.html", title="Login")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("login"))

# ===============================
#  USER: Dashboard & Complaint
# ===============================
@app.route("/dashboard")
def dashboard():
    if "user" not in session or session["role"] != "user":
        return redirect(url_for("login"))
    complaints = list(mongo.db.complaints.find())
    return render_template("dashboard.html", title="My Complaints", complaints=complaints)

@app.route("/complaint", methods=["GET", "POST"])
def complaint():
    if "user" not in session or session["role"] != "user":
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]

        category = predict_category(description)
        dept_email = department_emails.get(category, "other@municipal.gov")

        complaint_doc = {
            "user": session["user"],
            "title": title,
            "description": description,
            "category": category,
            "department_email": dept_email,
            "status": "Pending",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        mongo.db.complaints.insert_one(complaint_doc)

        send_email(
            dept_email,
            category,
            f"New Complaint: {title}",
            f"A new complaint has been filed:\n\n"
            f"Title: {title}\nCategory: {category}\nDescription: {description}\nUser: {session['user']}"
        )

        flash(f"Complaint submitted under '{category}' category.")
        return redirect(url_for("dashboard"))

    return render_template("complaint.html", title="File Complaint")

# ==========================================
# ADMIN: Dashboard, Update, Delete
# ==========================================
@app.route("/admin")
def admin_dashboard():
    if "user" not in session or session["role"] != "admin":
        return redirect(url_for("login"))
    complaints = list(mongo.db.complaints.find())
    return render_template("admin.html", title="Admin Dashboard", complaints=complaints)

@app.route("/update/<complaint_id>", methods=["POST"])
def update_status(complaint_id):
    if "user" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    new_status = request.form["status"]
    mongo.db.complaints.update_one({"_id": ObjectId(complaint_id)}, {"$set": {"status": new_status}})
    flash("Complaint status updated.")
    return redirect(url_for("admin_dashboard"))

#  NEW: DELETE COMPLAINT FEATURE
@app.route("/delete/<complaint_id>", methods=["POST"])
def delete_complaint(complaint_id):
    if "user" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    try:
        result = mongo.db.complaints.delete_one({"_id": ObjectId(complaint_id)})
        if result.deleted_count > 0:
            flash("Complaint deleted successfully.")
        else:
            flash("Complaint not found.")
    except Exception as e:
        flash(f"Error deleting complaint: {str(e)}")

    return redirect(url_for("admin_dashboard"))

# ==========================================
# Run App
# ==========================================
if __name__ == "__main__":
    app.run(debug=True)
