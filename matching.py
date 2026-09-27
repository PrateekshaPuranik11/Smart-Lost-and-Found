"""
matching.py — the 'intelligence' of Smart Lost and Found.

Scores every new report against all reports of the opposite type
using three signals:
  1. Text similarity   (TF-IDF cosine on descriptions)   weight 0.5
  2. Location match    (same tagged location / distance)  weight 0.3
  3. Time proximity    (closer timestamps score higher)   weight 0.2

Final score is 0–1; anything >= 0.6 is shown as a 'strong match'.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import math

STRONG_MATCH_THRESHOLD = 0.60

# ---------------------------------------------------------------- text ----
def text_similarity(desc1, desc2):
    """Cosine similarity of two descriptions using TF-IDF (0 to 1)."""
    vec = TfidfVectorizer(stop_words="english")
    tfidf = vec.fit_transform([desc1, desc2])
    return float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])

# ------------------------------------------------------------- location ----
def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in km between two lat/lon points."""
    R = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))

def location_score(loc1, loc2, lat1=None, lon1=None, lat2=None, lon2=None):
    """1.0 for identical location tags, otherwise fades by distance (2 km = 0)."""
    if loc1 == loc2:
        return 1.0
    if None in (lat1, lon1, lat2, lon2):
        return 0.2  # unknown coordinates: small partial credit, same campus
    d = haversine_km(lat1, lon1, lat2, lon2)
    return max(0.0, 1.0 - d / 2.0)

# ----------------------------------------------------------------- time ----
def time_score(t1, t2, max_hours=72):
    """1.0 if same moment, linearly down to 0 after `max_hours`."""
    hours = abs((t1 - t2).total_seconds()) / 3600
    return max(0.0, 1.0 - hours / max_hours)

# ------------------------------------------------------------ combined ----
def match_score(new_report, candidate, w_text=0.5, w_loc=0.3, w_time=0.2):
    ts = text_similarity(new_report["description"], candidate["description"])
    ls = location_score(
        new_report["location"], candidate["location"],
        new_report.get("lat"), new_report.get("lon"),
        candidate.get("lat"), candidate.get("lon"),
    )
    tms = time_score(new_report["time"], candidate["time"])
    score = w_text * ts + w_loc * ls + w_time * tms
    breakdown = {"text": round(ts, 3), "location": round(ls, 3), "time": round(tms, 3)}
    return round(score, 3), breakdown

def find_matches(new_report, all_reports, top_n=5):
    """Rank all opposite-type reports against `new_report`; return top_n."""
    opposite = "found" if new_report["type"] == "lost" else "lost"
    scored = []
    for cand in all_reports:
        if cand["type"] != opposite:
            continue
        score, breakdown = match_score(new_report, cand)
        scored.append({**cand, "score": score, "breakdown": breakdown})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]
