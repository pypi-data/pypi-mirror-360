from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)

#Globals
seasons = [
    '20102011',
    '20112012',
    '20122013',
    '20132014',
    '20142015',
    '20152016',
    '20162017',
    '20172018',
    '20182019',
    '20192020',
    '20202021',
    '20212022', 
    '20222023',
    '20232024',
    '20242025'
]

#Generate pages
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about/about")
def about():
    return render_template("about/about.html")

@app.route("/about/glossary")
def glossary():
    return render_template("about/glossary.html")

@app.route("/about/goal_impact")
def goal_impact():
    return render_template("about/goal_impact.html")

@app.route("/about/resources")
def resources():
    return render_template("about/resources.html")

@app.route("/about/xg_model")
def xg_model():
    return render_template("about/xg_model.html")

@app.route("/games/schedule")
def schedule():
    return render_template("games/schedule.html")

@app.route("/games/game_metrics")
def pbp_viewer():
    return render_template("games/game_metrics.html")

@app.route("/players/skater_stats", methods=["GET", "POST"])
def skater_stats():
    filters = {}
    for filter in ['season','span','strength','position','display','type','min_age','min_toi']:
        print(request.args.get(filter))
        filters.update({filter:request.args.get(filter)})

    return render_template("players/skater_stats.html")

@app.route("/players/goalie_stats")
def goalie_stats():
    return render_template("players/goalie_stats.html")

@app.route("/players/team_stats")
def team_stats():
    return render_template("players/team_stats.html")

if __name__ == "__main__":
    app.run()