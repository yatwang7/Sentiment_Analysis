from transformers import AutoTokenizer, AutoModelForSequenceClassification
from collections import Counter
import torch
import re
import nltk
from nltk.stem import WordNetLemmatizer

# ----------- Setup NLTK -----------
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
    nltk.download('omw-1.4')

lemmatizer = WordNetLemmatizer()

# ----------- Load Transformer Model -----------
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
_tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
_model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
_LABELS = ["negative", "neutral", "positive"]

# ----------- Question Detection Heuristics -----------
WH_WORDS = {"what","why","how","when","where","which","who","whom","whose"}
AUX_START = {"is","are","was","were","do","does","did","can","could","should",
             "would","will","has","have","had"}
QUESTION_PHRASES = {
    "anyone know","should i take","who to take","how is","is x good",
    "is this class hard","thoughts on","recommendations for","worth taking",
    "has anyone taken","which section","which professor","need advice"
}
REVIEW_HINTS = {
    "i took","i had","i’ve had","i have had","took him","took her","took with",
    "he taught","she taught","was taught","graded","curve","lectures","assignments",
    "homework","midterms","exams","quizzes","labs","projects","helpful","clear",
    "organized","engaging","caring","fair","hard","easy","attendance","office hours"
}

def is_question_like(review: str) -> bool:
    """
    Return True if the text is primarily a question rather than a review.
    """
    r = (review or "").strip().lower()
    score = 0
    if "?" in r: score += 1
    first_word = re.split(r"\W+", r)[0] if r else ""
    if first_word in WH_WORDS or first_word in AUX_START: score += 2
    if any(p in r for p in QUESTION_PHRASES): score += 1
    if any(p in r for p in REVIEW_HINTS): score -= 1
    return score >= 2

# ----------- Utility Functions -----------

def normalize(word):
    """Normalize a word by lemmatizing it."""
    return lemmatizer.lemmatize(word)

def clean_text(text):
    """Lowercase and remove punctuation."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text

# ----------- Transformer Sentiment Analysis -----------

def analyze_sentiment(review_text):
    """
    Analyze sentiment using transformer model.
    Returns polarity [-1, 1] and subjectivity [0, 1].
    """
    if not review_text:
        return {"polarity": 0.0, "subjectivity": 0.0}

    inputs = _tokenizer(review_text, return_tensors="pt", truncation=True, max_length=256)
    with torch.no_grad():
        logits = _model(**inputs).logits[0]
        probs = torch.softmax(logits, dim=0).cpu().numpy()  # [neg, neu, pos]

    neg, neu, pos = map(float, probs)
    polarity = pos - neg  # convert to [-1, 1]
    subjectivity = 1.0 - neu  # less neutral → more subjective

    return {"polarity": polarity, "subjectivity": subjectivity}

# ----------- Summary Extraction -----------

def summarize_reviews(review_list, prof_name, top_n=5):
    """
    Summarize common themes in the reviews by extracting frequent words.
    """
    stop_words = {
        "a", "an", "the", "is", "are", "was", "were", "be", "to", "of", "and",
        "in", "for", "with", "on", "this", "that", "i", "it", "but", "they",
        "she", "he", "we", "you", "about", "very", "have", "has", "had", "my",
        "so", "at", "his", "her", "their", "our", "as", "not", "from", "or",
        "like", "will", "just", "if", "all", "what", "when", "which", "who",
        "there", "out", "up", "more", "no", "one", "would", "been", "some",
        "could", "did", "how", "than", "then", "take", "class", "course",
        "professor", "prof", "dr", "doctor", "also", "anyone", "semester",
        "took", "your",
        prof_name.lower()
    }

    all_words = []
    for review in review_list:
        if is_question_like(review):
            continue
        cleaned = clean_text(review)
        tokens = [normalize(word) for word in cleaned.split()]
        meaningful = [w for w in tokens if w not in stop_words and len(w) > 3]
        all_words.extend(meaningful)

    if not all_words:
        return "No significant common themes found."

    common_words = Counter(all_words).most_common(top_n)
    return ", ".join([w for w, _ in common_words])

# ----------- Average Polarity Calculation -----------

def average_polarity_from(results, scheme="objective", eps=1e-9):
    """
    Compute weighted average polarity.
    scheme:
      - 'objective': weight = 1 - subjectivity (trust objective reviews more)
      - 'subjective': weight = subjectivity
      - 'flat': weight = 1
      - 'soft': weight = 1 - subjectivity^2
    """
    if not results:
        return 0.0

    polys = [r["polarity"] for r in results]
    subjs = [r["subjectivity"] for r in results]

    if scheme == "objective":
        weights = [max(0.0, 1.0 - s) for s in subjs]
    elif scheme == "subjective":
        weights = [max(0.0, s) for s in subjs]
    elif scheme == "soft":
        weights = [max(0.0, 1.0 - (s**2)) for s in subjs]
    else:
        weights = [1.0] * len(polys)

    wsum = sum(weights)
    if wsum <= eps:
        return sum(polys) / len(polys)
    return sum(w * p for w, p in zip(weights, polys)) / wsum

# ----------- Filter Most Polarizing Reviews -----------

def select_most_polarizing(sentiments, top_k,
                           min_abs_polarity=0.25,
                           min_subjectivity=0.15):
    """
    Keep the 'top_k' most polarizing reviews.
    We score each review by:
        score = |polarity| * (0.5 + 0.5 * subjectivity)
    This prioritizes extreme polarity and slightly downweights highly neutral items.
    Filters out items below thresholds before ranking.

    Args:
        sentiments: list of dicts with keys 'review','polarity','subjectivity'
        top_k: how many to keep
        min_abs_polarity: minimal absolute polarity required
        min_subjectivity: minimal subjectivity (avoid ultra-neutral texts)

    Returns:
        list[dict]: top_k most polarizing reviews
    """
    # pre-filter
    filtered = [
        s for s in sentiments
        if abs(s["polarity"]) >= min_abs_polarity and s["subjectivity"] >= min_subjectivity
    ]

    # score by polarization (more subjective → slightly higher score)
    def polar_score(s):
        return abs(s["polarity"]) * (0.5 + 0.5 * s["subjectivity"])

    ranked = sorted(filtered, key=polar_score, reverse=True)
    return ranked[:top_k] if top_k > 0 else ranked


# ----------- Main Review Analysis -----------

def analyze_reviews(review_list, prof_name, top_k_polarizing):
    """
    Analyze all reviews: filter questions, run sentiment,
    compute average polarity and summary, then keep only the most polarizing reviews.
    """
    results = []
    for review in review_list:
        if is_question_like(review):
            continue
        sentiment = analyze_sentiment(review)
        results.append({
            "review": review,
            "polarity": sentiment["polarity"],
            "subjectivity": sentiment["subjectivity"]
        })

    # Summary from the full (non-question) set for stability
    summary = summarize_reviews(review_list, prof_name)

    # Average polarity computed over all non-question results
    results = select_most_polarizing(
        results,
        top_k=top_k_polarizing * 2,
        min_abs_polarity=0.25,
        min_subjectivity=0.15
    )
    average_polarity = average_polarity_from(results, scheme="objective")

    # --- Keep only the most polarizing items
    results = select_most_polarizing(
        results,
        top_k=top_k_polarizing,
        min_abs_polarity=0.25,
        min_subjectivity=0.15
    )

    return {
        "sentiments": results,
        "average_polarity": average_polarity,
        "summary": summary
    }

# ----------- Example Usage -----------
if __name__ == "__main__":
    sample_reviews = [
        "This professor is amazing and very helpful.",
        "Lectures are clear and well-structured.",
        "Assignments are a bit tough, but fair.",
        "She cares about students and explains concepts well.",
        "Hard exams, but learned a lot!",
        "Should I take him for CS205?"
    ]

    analysis = analyze_reviews(sample_reviews, "SampleProfessor")

    print("Average Polarity:", round(analysis["average_polarity"], 3))
    print("\nSummary of Common Themes:")
    print(analysis["summary"], "\n")

    for r in analysis["sentiments"]:
        print(f"Review: {r['review']}")
        print(f"Polarity: {r['polarity']:.3f}, Subjectivity: {r['subjectivity']:.3f}\n")
