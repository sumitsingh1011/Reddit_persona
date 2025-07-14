import os
from flask import Flask, render_template, request
from persona_builder import scrape_reddit_user, generate_persona_from_data, save_json

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"].strip()
        user_data = scrape_reddit_user(username)
        save_json(user_data, f"data/{username}.json")
        persona_text = generate_persona_from_data(user_data)
        return render_template("persona.html", username=username, persona=persona_text, data=user_data)
    return render_template("index.html")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # use the PORT Render sets
    app.run(host="0.0.0.0", port=port)        # bind to 0.0.0.0 so Render can reach it

