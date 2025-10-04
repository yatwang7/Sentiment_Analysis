from textblob import TextBlob

def analyze_sentiment(review_text):
    """
    Analyzes sentiment of a single review using TextBlob.
    Returns a dictionary with polarity and subjectivity.
    """
    blob = TextBlob(review_text)
    sentiment = blob.sentiment
    return {
        "polarity": sentiment.polarity,         # range: [-1.0, 1.0]
        "subjectivity": sentiment.subjectivity  # range: [0.0, 1.0]
    }

def analyze_reviews(review_list):
    """
    Takes a list of review strings and returns a list of dictionaries
    with sentiment scores for each.
    """
    results = []
    for review in review_list:
        sentiment = analyze_sentiment(review)
        results.append({
            "review": review,
            "polarity": sentiment["polarity"],
            "subjectivity": sentiment["subjectivity"]
        })
    return results

# Example usage
if __name__ == "__main__":
    sample_reviews = [
        "This professor was amazing and really cared about students.",
        "The lectures were confusing and hard to follow.",
        "Pretty average, nothing great, nothing bad.",
    ]
    
    results = analyze_reviews(sample_reviews)
    for r in results:
        print(f"Review: {r['review']}")
        print(f"Polarity: {r['polarity']:.2f}, Subjectivity: {r['subjectivity']:.2f}\n")
