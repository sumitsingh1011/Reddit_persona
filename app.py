
from flask import Flask, render_template, request
from persona_builder import (
    scrape_reddit_user,
    generate_persona_from_data,
    save_json,
    save_persona_text,
)

import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
 return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    username = request.form.get("username")
    print(f"Received username: {username}")  # Debug log

    try:
        user_data = scrape_reddit_user(username)
        print("✅ Reddit data scraped.")

        persona = generate_persona_from_data(user_data)
        print("✅ Persona generated.")

        if persona:
            filename_safe = username.replace("/", "_")
            save_json(user_data, f"data/{filename_safe}.json")
            save_persona_text(persona, filename_safe)
            print("✅ Persona and JSON saved.")

            return render_template(
                "result.html", persona=persona, username=username, data=user_data
            )
        else:
            print("❌ Persona generation failed.")
            return "Failed to generate persona", 500

    except Exception as e:
        print("🔥 Error in /generate:", e)
        return f"Internal server error: {e}", 500

# === Ensure proper port binding for Render ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render uses this env var
    app.run(host="0.0.0.0", port=port)
