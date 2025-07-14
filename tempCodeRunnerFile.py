reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
     check_for_async=False  
)
print(reddit.read_only)

openai.api_key = OPENAI_API_KEY
