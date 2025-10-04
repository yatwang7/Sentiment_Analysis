from textblob import TextBlob
from collections import Counter
import re
import nltk
from nltk.stem import WordNetLemmatizer

# Download once
nltk.download('wordnet')
nltk.download('omw-1.4')  # optional but improves accuracy

lemmatizer = WordNetLemmatizer()

WH_WORDS = {"what","why","how","when","where","which","who","whom","whose"}
AUX_START = {"is","are","was","were","do","does","did","can","could","should","would","will","has","have","had"}
QUESTION_PHRASES = {
    "anyone know","should i take","who to take","how is","is x good",
    "is this class hard","thoughts on","recommendations for","worth taking",
    "has anyone taken","which section","which professor","need advice"
}
REVIEW_HINTS = {
    # signals of past/experience-based reviews
    "i took","i had","i’ve had","i have had","took him","took her","took with",
    "he taught","she taught","was taught","graded","curve","lectures","assignments",
    "homework","midterms","exams","quizzes","labs","projects","helpful","clear",
    "organized","engaging","caring","fair","hard","easy","attendance","office hours"
}

def is_question_like(review):
    """
    Return True if the post is primarily a question (not a review).
    Simple scoring heuristic on title + body (title weighted).
    """
    r = (review or "").strip().lower()

    # Quick positives for question-ness
    score = 0
    if "?" in r: score += 1

    # Starts with WH/Aux pattern?
    first_word = re.split(r"\W+", r)[0] if r else ""
    if first_word in WH_WORDS or first_word in AUX_START:
        score += 2

    # Phrase matches
    if any(p in r for p in QUESTION_PHRASES): score += 1

    # Penalize if we see strong review hints (experience/past tense/etc.)
    if any(p in r for p in REVIEW_HINTS): score -= 1

    # Tuneable threshold
    return score >= 2

def normalize(word):
    """
    Normalize words by lemmatization.
    """
    return lemmatizer.lemmatize(word)

def clean_text(text):
    """
    Cleans the input text by lowering case and removing punctuation.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text) # Remove punctuation
    return text

def analyze_sentiment(review_text):
    """
    Analyzes sentiment of the review text using TextBlob.
    Returns polarity and subjectivity.
    Polarity is a float within the range [-1.0, 1.0] where -1 indicates negative sentiment and +1 indicates positive sentiment.
    Subjectivity is a float within the range [0.0, 1.0] where 0.0 is very objective and 1.0 is very subjective.
    """
    blob = TextBlob(review_text)
    return {
        "polarity": blob.sentiment.polarity,
        "subjectivity": blob.sentiment.subjectivity
    }

def summarize_reviews(review_list, prof_name, top_n=5):
    """
    Summarizes common words/themes in the reviews.
    Returns top N most common meaningful words.
    """
    # Identify and exclude common stop words and review-specific terms
    stop_words = {
        "a", "an", "the", "is", "are", "was", "were", "be", "to", "of", "and", "in",
        "for", "with", "on", "this", "that", "i", "it", "but", "they", "she", "he",
        "we", "you", "about", "very", "have", "has", "had", "my", "so", "at", "his",
        "her", "their", "our", "as", "not", "from", "or", "like", "will", "just", "your"
        "if", "all", "what", "when", "which", "who", "there", "out", "up", "more",
        "no", "one", "would", "been", "some", "could", "did", "how", "than", "then",
        "take", "class", "course", "professor", "prof", "dr", "doctor", prof_name.lower()
    }

    # Analyze each review and collect meaningful words
    all_words = []
    for review in review_list:
        cleaned = clean_text(review)
        cleaned_normalized = [normalize(word) for word in cleaned.split()]
        meaningful = [word for word in cleaned_normalized if word not in stop_words and len(word) > 3]
        all_words.extend(meaningful)

    # Get the top N most common words
    word_freq = Counter(all_words)
    common_words = word_freq.most_common(top_n)
    summary = ", ".join([word for word, freq in common_words])
    return summary

def analyze_reviews(review_list, prof_name):
    """
    Analyze sentiment and return results with a summary.
    """
    # Polarity and subjectivity for each review
    results = []
    for review in review_list:
        if is_question_like(review):
            continue  # Skip question-like posts
        sentiment = analyze_sentiment(review)
        results.append({
            "review": review,
            "polarity": sentiment["polarity"],
            "subjectivity": sentiment["subjectivity"]
        })
    # Summary of all reviews
    summary = summarize_reviews(review_list, prof_name)

    # Average polairity taking into account subjectivity
    if results:
        weights = [max(0.0, 1.0 - r["subjectivity"]) for r in results]  # trust objective reviews more
        weighted_sum = sum(r["polarity"] * w for r, w in zip(results, weights))
        total_weight = sum(weights) if sum(weights) > 0 else 1
        average_polarity = weighted_sum / total_weight
    else:
        average_polarity = 0.0

    return {
        "sentiments": results,
        "average_polarity": average_polarity,
        "summary": summary
    }

# Example usage
if __name__ == "__main__":
    sample_reviews = [
        "This professor is amazing and very helpful.",
        "Lectures are clear and well-structured.",
        "Assignments are a bit tough, but fair.",
        "She cares about students and explains concepts well.",
        "Hard exams, but learned a lot!"
    ]

    analysis = analyze_reviews(sample_reviews)

    for r in analysis["sentiments"]:
        print(f"Review: {r['review']}")
        print(f"Polarity: {r['polarity']:.2f}, Subjectivity: {r['subjectivity']:.2f}\n")

    print("Summary of Common Themes:")
    print(analysis["summary"])
