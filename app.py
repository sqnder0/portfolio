from flask import Flask, render_template
from flask import request
from utils import Database, Email
import wikipedia

app = Flask(__name__, static_url_path="", static_folder='static')

app.config["TEMPLATE_AUTO_RELOAD"] = True

db = Database("portfolio.db")

@app.route("/", methods=["GET", "POST"])
def index():
    
    if request.method == "POST":
        try:
            form_data = {
                "first_name": request.args.get("fname"),
                "company": request.args.get("cname"),
                "last_name": request.args.get("lname"),
                "phone_number": request.args.get("phone"),
                "email": request.args.get("email"),
                "details": request.args.get("details"),
            }
            
            message = f"""Hey {form_data['first_name']} {form_data['last_name']}
            We have received following details:
            You work at: {form_data["company"]}
            Your phone number is: {form_data["phone_number"]}
            And wanted to tell us: {form_data["details"]}"""
            
            mail = Email(receiver=form_data["email"], text=message)
            
            mail.send()
            
            for card in cards:
                card["innerText"] = wikipedia.summary(card["wiki"], sentences=2)
                
            return render_template("index.html", cards=cards, message="We received your contact information")
            
        except Exception as e:
            print(e)
            error = {
                "code": 422,
                "description": "Unprocessable Entity, invalid form data"
            }
            cards = db.execute("SELECT * FROM tools;")
            for card in cards:
                card["innerText"] = wikipedia.summary(card["wiki"], sentences=2)
            return render_template("index.html", cards=cards, message="422 Unprocessable Entity, invalid form data")
        
    cards = db.execute("SELECT * FROM tools;")
    for card in cards:
        card["innerText"] = wikipedia.summary(card["wiki"], sentences=2)
    return render_template("index.html", cards=cards)