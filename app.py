from flask import Flask, render_template, request, jsonify
from scrape_reviews import get_reddit_reviews
from sentiment_analysis import analyze_reviews
import os
import json

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
    
    # First check if sentiment analysis results already exist
    output_file = f"data/{prof_name.replace(' ', '_')}_analysis.json"
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        return jsonify(results)
    
    # Scrape Reddit posts
    print("Scraping Reddit for professor:", prof_name)
    review_texts = get_reddit_reviews(prof_name, "Rutgers University", limit_per_subreddit=20)

    if not review_texts:
        return jsonify({"error": f"No Reddit posts found for {prof_name}"}), 404

    # Run sentiment analysis
    results = analyze_reviews(review_texts, prof_name, top_k_polarizing=10)

    # Save results to JSON
    output_file = f"data/{prof_name.replace(' ', '_')}_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"[Saved] Analysis results saved to {output_file}")
    
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
