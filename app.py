"""
app.py — Flask application for Smart Lost and Found.

Run:  python app.py
Then open http://127.0.0.1:5000

Routes:
  GET  /                 home + all reports
  GET  /report/new       submission form (lost or found)
  POST /report/new       save report -> auto-match -> show ranked matches
  GET  /matches/<id>     re-view matches for an existing report
  POST /verify/<id>      mark a report as verified (owner confirmed match)
"""
import os
from datetime import datetime
from flask import (Flask, request, redirect, render_template, url_for, flash)
from werkzeug.utils import secure_filename

import db
from matching import find_matches, STRONG_MATCH_THRESHOLD

app = Flask(__name__)
app.secret_key = "hackathon-secret-change-me"
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif"}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
db.init_db()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def reports_as_match_input():
    return [db.to_match_input(r) for r in db.all_reports()]

@app.route("/")
def home():
    return render_template("index.html", reports=db.all_reports(),
                           locations=db.CAMPUS_LOCATIONS)

@app.route("/report/new", methods=["GET", "POST"])
def new_report():
    if request.method == "POST":
        f = request.form
        image_path = None
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                image_path = os.path.join("uploads", filename)

        try:
            report_time = datetime.fromisoformat(f["time"])
        except ValueError:
            report_time = datetime.now()

        lat = float(f["lat"]) if f.get("lat") else None
        lon = float(f["lon"]) if f.get("lon") else None

        data = {
            "type": f["type"],
            "title": f["title"].strip(),
            "description": f["description"].strip(),
            "location": f["location"],
            "lat": lat, "lon": lon,
            "time": report_time,
            "image_path": image_path,
            "contact": f["contact"].strip(),
        }
        new_id = db.insert_report(data)

        # ----- the "smart" part: match against all opposite-type reports -----
        fresh = db.to_match_input(db.get_report(new_id))
        matches = find_matches(fresh, reports_as_match_input())
        strong = [m for m in matches if m["score"] >= STRONG_MATCH_THRESHOLD]
        if strong:
            db.set_status(new_id, "matched")

        return render_template("matches.html", report=fresh, matches=matches,
                               threshold=STRONG_MATCH_THRESHOLD, strong_count=len(strong))

    return render_template("report_form.html", locations=db.CAMPUS_LOCATIONS)

@app.route("/matches/<int:report_id>")
def view_matches(report_id):
    report = db.to_match_input(db.get_report(report_id))
    matches = find_matches(report, reports_as_match_input())
    return render_template("matches.html", report=report, matches=matches,
                           threshold=STRONG_MATCH_THRESHOLD,
                           strong_count=sum(1 for m in matches if m["score"] >= STRONG_MATCH_THRESHOLD))

@app.route("/verify/<int:report_id>", methods=["POST"])
def verify(report_id):
    db.set_status(report_id, "verified")
    flash(f"Report #{report_id} marked as verified — item reunited!")
    return redirect(url_for("home"))

if __name__ == "__main__":
    if __name__ == "__main__":
     app.run(debug=False)
