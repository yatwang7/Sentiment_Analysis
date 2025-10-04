from textblob import TextBlob
from collections import Counter
import re
import nltk
from nltk.stem import WordNetLemmatizer

# Download once
nltk.download('wordnet')
nltk.download('omw-1.4')  # optional but improves accuracy

lemmatizer = WordNetLemmatizer()

def normalize(word):
    return lemmatizer.lemmatize(word)

def clean_text(text):
    # Basic text cleaning for keyword extraction
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # remove punctuation
    return text

def analyze_sentiment(review_text):
    blob = TextBlob(review_text)
    return {
        "polarity": blob.sentiment.polarity,
        "subjectivity": blob.sentiment.subjectivity
    }

def summarize_reviews(review_list, top_n=5):
    """
    Summarizes common words/themes in the reviews.
    Returns top N most common meaningful words.
    """
    all_words = []
    stop_words = {
        "a", "an", "the", "is", "are", "was", "were", "be", "to", "of", "and",
        "in", "for", "with", "on", "this", "that", "i", "it", "but", "they",
        "she", "he", "we", "you", "about", "very", "have", "has", "had", "my",
        "so", "at", "his", "her", "their", "our", "as", "not", "from", "or"
    }
    common_review_words = {"professor", "course", "class", "lecture", "assignment", "exam", "student", "students"}
    exclude_words = stop_words | common_review_words

    for review in review_list:
        cleaned = clean_text(review)
        cleaned_normalized = [normalize(word) for word in cleaned.split()]
        meaningful = [word for word in cleaned_normalized if word not in exclude_words and len(word) > 3]
        all_words.extend(meaningful)

    word_freq = Counter(all_words)
    common_words = word_freq.most_common(top_n)
    summary = ", ".join([word for word, freq in common_words])
    return summary

def analyze_reviews(review_list):
    """
    Analyze sentiment and return results with a summary.
    """
    results = []
    for review in review_list:
        sentiment = analyze_sentiment(review)
        results.append({
            "review": review,
            "polarity": sentiment["polarity"],
            "subjectivity": sentiment["subjectivity"]
        })

    summary = summarize_reviews(review_list)
    return {
        "sentiments": results,
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
