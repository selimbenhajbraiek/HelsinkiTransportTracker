import os
from flask import Flask, jsonify, render_template
from flask_migrate import Migrate
from models import db

# Create Flask app
app = Flask(__name__, 
           static_folder="app/static",
           template_folder="app/templates")

# Load environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")

# Configure app
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.environ.get("SESSION_SECRET", "helsinki_transport_secret_key")

# Initialize SQLAlchemy with app
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Create all tables
with app.app_context():
    db.create_all()

# Routes
@app.route("/")
def index():
    """Root route showing main interface"""
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    """Dashboard showing statistics"""
    return render_template("dashboard.html")

@app.route("/api/health")
def health_check():
    """API health check endpoint"""
    return jsonify({"status": "OK", "message": "Server is running"})

# This is needed for direct execution
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)