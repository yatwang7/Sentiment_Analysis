import praw

# ----------- Setup Reddit API -----------
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="YOUR_USER_AGENT"
)

# ----------- Function to search for comments/posts -----------
def get_reddit_reviews(name, school, limit=20):
    query = f'"{name}" "{school}"'
    reviews = []

    try:
        for submission in reddit.subreddit("all").search(query, limit=limit):
            # Add submission title + selftext if present
            text = submission.title
            if submission.selftext:
                text += "\n" + submission.selftext
            reviews.append(text)

            # Add top-level comments
            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():
                reviews.append(comment.body)

        print(f"[Reddit] Collected {len(reviews)} items")
        return reviews

    except Exception as e:
        print(f"[Reddit] Error: {e}")
        return []

# ----------- Main -----------
if __name__ == "__main__":
    professor_name = "David Menedez"
    professor_school = "Rutgers University"

    reviews = get_reddit_reviews(professor_name, professor_school, limit=10)
    print("\nSample reviews:\n")
    for r in reviews[:5]:
        print("-", r, "\n")
