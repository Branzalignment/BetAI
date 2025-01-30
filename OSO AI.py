from flask import Flask, jsonify, render_template
import requests
import os
import time
import random

app = Flask(__name__)

# Update API_URL to use the provided Container URL with Apify token
API_URL = "https://api.apify.com/v2/datasets/49G0FpM1tuOTfXgab/items?clean=true&format=json"


def ensure_templates_dir():
    """Ensure the templates directory exists and creates index.html."""
    if not os.path.exists("templates"):
        os.makedirs("templates")
    if not os.path.exists("templates/index.html"):
        with open("templates/index.html", "w") as f:
            f.write(html_template)


def fetch_data():
    """Fetch data from the API with a delay to ensure data is ready."""
    time.sleep(120)  # Wait for 2 minutes to allow the API to populate data
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json()


@app.route("/")
def index():
    try:
        ensure_templates_dir()

        # Fetch data from the API
        data = fetch_data()
        print(f"Data fetched: {data[:5]}")  # Debug: Check if data is what you expect

        # Filter games based on specified conditions
        eligible_games = [
            game for game in data
            if (
                    game.get("Bet_choice", "").lower() in ["1", "2", "btts yes"]
                    and 1.10 <= float(game.get("Bet_odds", "0.0")) <= 1.90
            )
        ]

        # Limit to 100-200 eligible games
        eligible_games = eligible_games[:200]

        # Randomly pick 5 games whose total odds are between 3 and 4.5
        selected_games = []
        for _ in range(100):
            if len(eligible_games) < 5:
                break
            random_games = random.sample(eligible_games, 5)
            total_odds = sum(float(game.get("Bet_odds", "0.0")) for game in random_games)
            if 3 <= total_odds <= 4.5:
                selected_games = random_games
                break

        # Handle case where no games meet the criteria
        if not selected_games:
            return render_template("index.html",
                                   message="No games found matching the criteria. Try adjusting the odds filters.")

        return render_template("index.html", games=selected_games)
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)})


# HTML template for displaying games
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSO Bet Predictions</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            padding: 20px;
            background-color: #f4f4f9;
            color: #333;
        }
        h1 {
            color: #0056b3;
        }
        .game {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
            background: #fff;
        }
    </style>
</head>
<body>
    <h1>OSO Bet Predictions</h1>
    {% if games %}
        {% for game in games %}
        <div class="game">
            <p><strong>Match:</strong> {{ game["Event_name"] or game["event_name"] or "Event Not Available" }}</p>
            <p><strong>Bet Choice:</strong> 
                {% if game["Bet_choice"] == "1" %}
                    Home Win
                {% elif game["Bet_choice"] == "2" %}
                    Away Win
                {% elif game["Bet_choice"].lower() == "btts yes" %}
                    BTTS Yes
                {% else %}
                    {{ game["Bet_choice"] }}
                {% endif %}
            </p>
   github         <p><strong>Odds:</strong> {{ game["Bet_odds"] or game["bet_odds"] or "N/A" }}</p>
        </div>
        {% endfor %}
    {% else %}
        <p>{{ message | default("No games found matching the criteria.") }}</p>
    {% endif %}
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)