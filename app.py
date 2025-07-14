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
    app.run(debug=True)
