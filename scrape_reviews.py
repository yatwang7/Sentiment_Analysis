import praw

# ----------- Setup Reddit API -----------
reddit = praw.Reddit(
    client_id="c_7L21TyZKWf17VUsGmOag",
    client_secret="MivtP_Pv1ZampBd8x3bzUtzoQpptCQ",
    user_agent="SentimentAnalysisScrapper"
)

# ----------- Function to get Reddit reviews -----------
def get_reddit_reviews(name, school, limit_per_subreddit=20):
    """
    Search specific subreddits for posts and comments mentioning a professor and school.
    Returns a cleaned list of review texts.
    """
    reviews = []
    last_name = name.split()[-1]

    # Subreddits to search
    subreddits = ["Rutgers", "college", "Professors"]

    # Query variations
    queries = [
        f"{last_name} {school.split()[0]}",
        f"Professor {last_name}",
        f"Dr. {last_name}",
        f"{name} {school.split()[0]}"
    ]

    try:
        for sub in subreddits:
            subreddit = reddit.subreddit(sub)
            for query in queries:
                for submission in subreddit.search(query, limit=limit_per_subreddit):
                    # Collect submission text
                    text = submission.title
                    if submission.selftext:
                        text += "\n" + submission.selftext
                    reviews.append(text)

                    # Collect all comments
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments.list():
                        reviews.append(comment.body)

        # Clean duplicates and very short text
        clean_reviews = list({r.strip() for r in reviews if len(r.strip()) > 10})
        print(f"[Reddit] Total cleaned reviews: {len(clean_reviews)}")
        return clean_reviews

    except Exception as e:
        print(f"[Reddit] Error: {e}")
        return []

# ----------- Main -----------
if __name__ == "__main__":
    professor_name = "David Menedez"
    professor_school = "Rutgers University"

    reviews = get_reddit_reviews(professor_name, professor_school, limit_per_subreddit=10)

    print("\nSample reviews:\n")
    for r in reviews[:5]:
        print("-", r, "\n")
