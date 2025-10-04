from flask import Flask, render_template, request, jsonify
from scrape_reviews import get_reddit_reviews
from sentiment_analysis import analyze_reviews

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    prof_name = data.get('prof_name')

    if not prof_name:
        return jsonify({"error": "No professor name provided"}), 400

    # Scrape Reddit posts
    print("Scraping Reddit for professor:", prof_name)
    cleaned_reviews = get_reddit_reviews(prof_name, "Rutgers University", limit_per_subreddit=20)
    review_texts = cleaned_reviews.get('reviews', [])

    if not review_texts:
        return jsonify({"error": f"No Reddit posts found for {prof_name}"}), 404

    # Run sentiment analysis
    results = analyze_reviews(review_texts)
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
