from flask import Flask, render_template
from utils import Database

app = Flask(__name__, static_url_path="", static_folder='static')

app.config["TEMPLATE_AUTO_RELOAD"] = True

db = Database("portfolio.db")

@app.route("/")
def index():
    cards = db.execute("SELECT * FROM tools;")
    
    return render_template("index.html", cards=cards)