"""
seed_data.py — populate the DB with realistic demo reports so the
matching engine has something to work with on first run.

Run:  python seed_data.py
"""
from datetime import datetime, timedelta
import os
import db

SAMPLES = [
    # (type, title, description, location, hours_ago)
    ("found", "Black backpack", "Black Adidas backpack with a laptop inside, found on a bench on the first floor near the reading section.", "Library", 3),
    ("lost", "Adidas backpack lost", "I lost my black Adidas backpack containing my laptop and charger, was studying on the first floor.", "Library", 4),
    ("found", "Water bottle", "Blue steel water bottle with stickers on it, left at a cafeteria table.", "Cafeteria", 10),
    ("lost", "Lost my bottle", "Sky blue steel water bottle with anime stickers, probably left it in the cafeteria after lunch.", "Cafeteria", 11),
    ("found", "ID card", "Student ID card of a first-year student, found near the main gate on the pavement.", "Main Gate", 26),
    ("lost", "ID card missing", "Lost my student ID card somewhere between the main gate and the academic block.", "Main Gate", 27),
    ("found", "Earbuds case", "White wireless earbuds charging case found in the gym.", "Sports Complex", 50),
    ("lost", "Headphones lost", "Lost my red over-ear headphones, last seen at the sports complex during practice.", "Sports Complex", 48),
    ("found", "Notebook", "Physics notebook with handwritten notes, brown cover, found in Hostel A common room.", "Hostel A", 80),
    ("lost", "Umbrella", "Left a black folding umbrella in the parking lot near the two-wheeler stand.", "Parking Lot", 30),
]

def main():
    if os.path.exists(db.DB_PATH):
        os.remove(db.DB_PATH)
    db.init_db()
    now = datetime.now()
    for i, (typ, title, desc, loc, hrs) in enumerate(SAMPLES):
        db.insert_report({
            "type": typ, "title": title, "description": desc,
            "location": loc, "lat": None, "lon": None,
            "time": now - timedelta(hours=hrs, minutes=i * 7),
            "image_path": None, "contact": f"user{i+1}@college.edu",
        })
    print(f"Seeded {len(SAMPLES)} reports into {db.DB_PATH}")

if __name__ == "__main__":
    main()
