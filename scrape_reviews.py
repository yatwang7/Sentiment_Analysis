import praw
from dotenv import load_dotenv
import os
import json

# ----------- Load environment variables -----------
load_dotenv()
CLIENT_ID = os.getenv("client_id")
CLIENT_SECRET = os.getenv("client_secret")
USER_AGENT = os.getenv("user_agent")

# ----------- Setup Reddit API -----------
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

def get_reddit_reviews(name, school, limit_per_subreddit=20):
    reviews = []
    first_name = name.split()[0]
    last_name = name.split()[-1]
    subreddits = ["Rutgers"]    # subreddits that will be searched

    # these are the exact phrases we will search for
    queries = [
        f"{last_name}",  # Menendez
        f"{first_name} {last_name}"    # David Menendez
    ]

    try:
        for sub in subreddits:
            subreddit = reddit.subreddit(sub)
            for query in queries:
                for submission in subreddit.search(query, limit=limit_per_subreddit, sort='relevance'):
                    text = submission.title
                    if submission.selftext:
                        text += "\n" + submission.selftext
                    reviews.append(text)

                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments.list():
                        reviews.append(comment.body)

        # Filter and clean reviews
        filtered_reviews = [r for r in reviews if last_name.lower() in r.lower()]
        clean_reviews = list({r.strip() for r in filtered_reviews if len(r.strip()) > 10})
        print(f"[Reddit] Total cleaned reviews: {len(clean_reviews)}")

        return clean_reviews

    except Exception as e:
        print(f"[Reddit] Error: {e}")
        return []


def save_reviews_to_json(name, school, reviews, output_dir="data"):
    """Save scraped reviews into a JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/{name.replace(' ', '_')}_reviews.json"

    data = {
        "professor_name": name,
        "school": school,
        "total_reviews": len(reviews),
        "reviews": reviews
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"[Saved] Reviews saved to {filename}")


# ----------- Main -----------
if __name__ == "__main__":
    professor_name = "David Sorenson"
    professor_school = "Rutgers University"

    reviews = get_reddit_reviews(professor_name, professor_school, limit_per_subreddit=10)

    print("\nSample reviews:\n")
    for r in reviews[:5]:
        print("-", r, "\n")

    # Save results to JSON
    save_reviews_to_json(professor_name, professor_school, reviews)
