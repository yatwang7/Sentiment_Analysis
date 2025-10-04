import praw
from dotenv import load_dotenv
import os

load_dotenv()
CLIENT_ID   = os.getenv("client_id")
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
    last_name = name.split()[-1]
    subreddits = ["Rutgers"]

    queries = [
        f"{last_name}",
        f"{last_name} {school.split()[0]}",
        f"Professor {last_name}",
        f"Dr {last_name}"
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

        # Keep only texts that mention the professor
        filtered_reviews = [r for r in reviews if last_name.lower() in r.lower()]
        # Remove duplicates and very short texts
        clean_reviews = list({r.strip() for r in filtered_reviews if len(r.strip()) > 10})
        print(f"[Reddit] Total cleaned reviews: {len(clean_reviews)}")
        return clean_reviews

    except Exception as e:
        print(f"[Reddit] Error: {e}")
        return []



# ----------- Main -----------
if __name__ == "__main__":
    professor_name = "Tzvika Geft"
    professor_school = "Rutgers University"

    reviews = get_reddit_reviews(professor_name, professor_school, limit_per_subreddit=10)

    print("\nSample reviews:\n")
    for r in reviews[:5]:
        print("-", r, "\n")
