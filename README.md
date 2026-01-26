
This README provides an overview of the Grievance Portal, a Flask-based web application designed to automate the process of filing and managing public grievances using Machine Learning for automated category classification.

Grievance Portal
The Grievance Portal is a web-based platform that allows users to submit complaints regarding public services. The application automatically classifies the complaint into specific departments (e.g., Roads, Sanitation, Water) using a trained AI model and notifies the respective departments via email.


1. Features:

User Authentication: Secure registration and login system for both citizens and administrators.

AI-Powered Classification: Automatically predicts the complaint category (e.g., Electricity, Health, Transport) based on the user's description using a TF-IDF vectorizer and a classifier model.

Automated Notifications: Sends an automated email to the relevant department once a complaint is filed.

User Dashboard: Users can track the status of their submitted complaints (Pending, In Progress, or Resolved).

Admin Management: Administrators can view all complaints, update their status, and delete records.

Responsive UI: A modern, dark-themed interface built with Bootstrap and custom CSS.


2. Technology Stack:

Backend: Python, Flask

Database: MongoDB (via Flask-PyMongo)

Machine Learning: Scikit-learn (Joblib for model persistence)

Email Service: SMTPLIB (Gmail SMTP)

Frontend: HTML5, CSS3, Jinja2 Templates, Bootstrap



3. Project Structure:

Grievance_app/
├── app.py                  # Main Flask application logic
├── model/                  # Trained ML models and encoders
│   ├── complaint_classifier.pkl
│   ├── label_encoder.pkl
│   └── tfidf_vectorizer.pkl
├── static/
│   └── style.css           # Custom styling for the application
└── templates/              # Jinja2 HTML templates
    ├── layout.html         # Base layout for all pages
    ├── index.html          # Landing page
    ├── login.html          # Login page
    ├── register.html       # User registration page
    ├── dashboard.html      # User's complaint tracking
    ├── complaint.html      # Form to file a new grievance
    └── admin.html          # Admin management dashboard



4. Setup and Installation:

Clone the Repository:

Bash
git clone <repository-url>
cd Grievance_app
Install Dependencies:

Bash
pip install flask flask_pymongo werkzeug joblib scikit-learn
Database Configuration:

Update the MONGO_URI in app.py with your MongoDB Atlas connection string.

Email Configuration:

The system uses a Gmail App Password for notifications. Update the sender and password variables in the send_email function in app.py.

Run the Application:

Bash
python app.py
The app will be available at http://127.0.0.1:5000/.


5. Usage:

For Users
Register/Login: Create an account to access the dashboard.

File Complaint: Enter a title and a detailed description of the issue.

Track Status: View whether your complaint is being processed or resolved by the department.

For Admins
Access Dashboard: Log in with administrative credentials.

Manage Grievances: Review incoming complaints, update their status (e.g., from "Pending" to "Resolved"), or delete invalid entries.




