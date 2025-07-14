from dotenv import load_dotenv
import os
import praw
import json
from transformers import pipeline
import traceback
    

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
    check_for_async=False
)

def scrape_reddit_user(username, max_items=100):
    user = reddit.redditor(username)
    data = {
        "username": username,
        "profile_img": user.icon_img if hasattr(user, "icon_img") else None,
        "description": user.subreddit["public_description"] if hasattr(user, "subreddit") else "",
        "total_karma": user.link_karma + user.comment_karma,
        "posts": [],
        "comments": []
    }
    try:
        for submission in user.submissions.new(limit=max_items):
            data["posts"].append({
                "title": submission.title,
                "selftext": submission.selftext,
                "subreddit": str(submission.subreddit),
                "url": f"https://reddit.com{submission.permalink}"
            })

        for comment in user.comments.new(limit=max_items):
            data["comments"].append({
                "body": comment.body,
                "subreddit": str(comment.subreddit),
                "url": f"https://reddit.com{comment.permalink}"
            })
    except Exception as e:
        print(f"Error scraping user {username}: {e}")
    return data

def save_json(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

import requests

def generate_persona_from_data(user_data):
    prompt_base = (
        "Create a detailed persona of a Reddit user including traits, interests, tone, "
        "social or political leanings. Use example posts or comment URLs.\n\nUser data:\n"
    )
    trimmed_data = {
        "username": user_data["username"],
        "posts": user_data["posts"][:3],
        "comments": user_data["comments"][:3]
    }
    prompt = prompt_base + json.dumps(trimmed_data, indent=2)

    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "HTTP-Referer": "https://reddit-persona.onrender.com",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openrouter/openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a persona analyst."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
    
    print("Error generating persona:", repr(e))
    traceback.print_exc()
    return None



def save_persona_text(persona_text, username):
    os.makedirs("outputs", exist_ok=True)
    with open(f"outputs/{username}_persona.txt", "w", encoding="utf-8") as f:
        f.write(persona_text)
