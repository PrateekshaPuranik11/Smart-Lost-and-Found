# Smart Lost & Found (Hackathon Starter)

A campus platform where students report lost/found items and the system
**automatically suggests matches** using description text, location, and time.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python seed_data.py              # loads 10 realistic demo reports
python app.py                    # open http://127.0.0.1:5000
```

Try it: open the app, submit a "lost" report like
*"black Adidas backpack with laptop, Library"* and watch the ranked matches
appear with per-signal score bars.

## How matching works (the "intelligence")

`matching.py` scores every new report against all opposite-type reports:

| Signal       | Method                                   | Weight |
|--------------|------------------------------------------|--------|
| Description  | TF-IDF cosine similarity                 |  50%   |
| Location     | Same tag = 100%, else fades over 2 km    |  30%   |
| Time         | Linear decay over 72 hours               |  20%   |

Score >= 0.60 is flagged a **strong match** and the report status flips
to `matched`. Owners can then click **Verify & Reunite**.

## Project layout

```
app.py            Flask routes + report form + matching trigger
matching.py       scoring engine (pure functions, easy to demo/test)
db.py             SQLite layer (reports table)
seed_data.py      demo data
templates/        Bootstrap UI (home, form, matches with score bars)
static/uploads/   user photos
```

## Upgrade path (stretch goals for demo day)

1. **Smarter text**: swap TF-IDF for `sentence-transformers`
   (`all-MiniLM-L6-v2`) — matches "sky blue bottle" to "blue water bottle"
   even with zero shared words.
2. **Image similarity**: CLIP embeddings to compare uploaded photos.
3. **Email/SMS notifications** when a strong match appears.
4. **Map view** of reports using lat/lon.
