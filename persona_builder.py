# === 1. Imports and Env Setup ===
from dotenv import load_dotenv
import os
import praw
import json
from transformers import pipeline

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# === 2. Initialize Reddit ===
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
    check_for_async=False
)
print(reddit.read_only)


# === 3. Reddit Scraper ===
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



# === 4. Save JSON File ===
def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# === 5. Generate Persona with Local GPT-J ===
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

    # 🔒 Limit final prompt to 1000 characters to avoid model overflow
    prompt = prompt[:1000]

    try:
        generator = pipeline("text-generation", model="gpt2-medium")
        result = generator(prompt, max_new_tokens=300, temperature=0.7)
        return result[0]["generated_text"]
    except Exception as e:
        print("Error generating persona:", repr(e))
        return None

# === 6. Save Persona to Text File ===
def save_persona_text(persona_text, username):
    with open(f"outputs/{username}_persona.txt", "w", encoding="utf-8") as f:
        f.write(persona_text)


# === 7. Run End-to-End ===
if __name__ == "__main__":
    username = "WarDaddy-911"
    user_data = scrape_reddit_user(username)

    # Prevent folder errors by sanitizing filename
    filename_safe = username.replace("/", "_")

    save_json(user_data, f"data/{filename_safe}.json")

    persona = generate_persona_from_data(user_data)
    if persona:
        save_persona_text(persona, filename_safe)
        print(f"Persona generated and saved for {username}")
