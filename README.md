# 💬 Reddit Sentiment Analyzer

This project scrapes Reddit discussions about any **topic, person, product, or event** (at Rutgers) and performs **sentiment analysis** on the collected posts and comments.  
It summarizes what people are saying, identifies common themes, and calculates overall sentiment polarity scores — giving you a quick read on Reddit’s opinion landscape.

---

## 🚀 Features

- 🔍 **Reddit scraping** via the official Reddit API using **PRAW**
- 🧠 **Sentiment analysis** using TextBlob or transformer-based models (e.g., DistilBERT)
- ❓ **Question filtering** — automatically removes posts that are mostly inquiries or off-topic
- ⚖️ **Weighted average polarity** — computes a subjectivity-weighted sentiment score
- 💾 **Caching system** — stores analyzed results to avoid redundant computations
- 🖥️ **Interactive web interface (Flask + HTML/CSS/JS)** for entering topics and viewing analysis
- 🌈 **Visual output** — displays common themes and color-coded sample posts

---

## 🧱 Project Structure

```

.
├── app.py                    # Flask backend serving API + frontend
├── scrape_reviews.py         # Reddit scraper using PRAW
├── sentiment_analysis.py     # Sentiment analysis logic
├── requirements.txt          # Dependencies
├── templates/
│ └── index.html              # Frontend UI
├── data/
│ └── <topic>_analysis.json   # Locally cached analysis file
├── LICENSE
└── README.md

```

---

## ⚙️ Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/yatwang7/Sentiment_Analysis.git
cd reddit-sentiment-analyzer
```

### 2. Python env & deps

```bash
python -m venv .venv
source .venv/bin/activate          # (Windows) .venv\Scripts\activate
pip install -r requirements.txt
```

**requirements.txt (minimum):**

```
flask
praw
python-dotenv
nltk
transformers
torch
```

> On Apple Silicon/macOS, if `torch` fails, grab the platform-specific install command from pytorch.org.

### 3. Reddit API credentials

Create an app at [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) → **Create App** → type **script**.
Copy `client_id`, `client_secret`, and set a `user_agent` (any descriptive string).

Create a `.env` file in the project root:

```env
client_id=YOUR_REDDIT_CLIENT_ID
client_secret=YOUR_REDDIT_CLIENT_SECRET
user_agent=professor-sentiment-app/0.1 by u/yourusername
```

### 4. Run the app

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) and try a topic.

---

## ⚙️ Configuration

### Subreddits & queries

In `scrape_reviews.py`, edit:

```python
subreddits = ["Rutgers"]    # add more if useful
limit_per_subreddit = 20    # adjust in app.py call or function arg
```

### Model

In `sentiment_analysis.py`:

```python
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
```

You can swap to another sentiment model if needed.

### Weights & caching

Transformers will download weights on first run to `~/.cache/huggingface`. First call may take a minute.

---

## 🧠 How It Works

### High-level flow

```
[Frontend index.html]
      |  (POST /analyze: {prof_name})
      v
[Flask app.py] -----> get_reddit_reviews(prof_name, ...)
      |                 (PRAW: gather titles, bodies, comments)
      |                 (optional: filter questions/noise)
      v
[analyze_reviews()] -> (transformer sentiment per review)
      |                (weighted avg polarity + summary)
      v
[JSON response] ----> Frontend renders summary + reviews
```

---

## 🧪 API

### `POST /analyze`

**Body (JSON):**

```json
{ "prof_name": "First Last" }
```

**Response (JSON):**

```json
{
  "sentiments": [
    { "review": "text...", "polarity": 0.62, "subjectivity": 0.33 }
  ],
  "average_polarity": 0.24,
  "summary": "helpful, clear, fair, engaging, tough"
}
```

---

## 🧩 Implementation Notes

* **Question filtering:** `is_question_like()` removes posts that are primarily asking for recommendations (“Should I take…?”).
* **Weighted average polarity:** objective-leaning texts (high neutrality) get **lower** weight; see `average_polarity_from(..., scheme="objective")`.
* **Most polarizing:** you can keep only the strongest opinions with `select_most_polarizing(...)` (optional; included in `sentiment_analysis.py` if you enabled it).
* **Caching:** after obtaining an analysis, we save it to a cache so the next lookup of the same topic is faster.

---

## 🧰 Troubleshooting

* **403 / CORS / fetch errors:**
  Ensure you’re opening [http://127.0.0.1:5000](http://127.0.0.1:5000) (not `file://…`). The frontend must call the Flask endpoint from the same origin.
* **PRAW auth errors:**
  Check `.env` values and that your Reddit app type is **script**. Regenerate secrets if needed.
* **Torch install issues:**
  Use the official install command for your OS/arch from [https://pytorch.org](https://pytorch.org).
* **Model download slow:**
  First run downloads weights; subsequent runs are cached.
* **Empty results:**
  Try a different professor string (full first + last). Increase `limit_per_subreddit`. Consider adding Rutgers-specific context words in `scrape_reviews.py`.

---

## 🔒 Ethics & Compliance

* Respect Reddit’s API terms and **rate limits**.
* Don’t store or display private data.
* Make it clear that results are **student opinions**, not facts.
* If deploying, add a simple **disclaimer** to the UI.

---

## 🧱 Roadmap (nice-to-haves)

* Add **dept/course inputs** to the UI; include them in search queries.
* Add **semantic relevance** (Sentence-BERT) to avoid name collisions.
* Visualize distribution with **Chart.js** (positive/neutral/negative bars).
* Cache per-query results to reduce API calls.
* Export CSV/JSON from the UI.

---

## 🤝 Contributing

1. Create a feature branch
2. Run `ruff`/`black` or your preferred formatter (optional)
3. Open a PR with a short demo (GIF/screenshot)

---

## 📘 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
