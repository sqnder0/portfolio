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
                "first_name": request.form.get("fname"),
                "company": request.form.get("cname"),
                "last_name": request.form.get("lname"),
                "phone_number": request.form.get("phone"),
                "email": request.form.get("email"),
                "details": request.form.get("details"),
            }
            
            message = f"""Hey {form_data['first_name']} {form_data['last_name']}\nWe have received following details:\nYou work at: {form_data["company"]}\nYour phone number is: {form_data["phone_number"]}\nAnd wanted to tell us: {form_data["details"]}"""
            
            mail = Email(subject="Hey, we received your submission!.", receiver=form_data["email"], body=message)
            mail.send()
            
            message = f"""Details:\nCompany: {form_data["company"]}\nName: {form_data["first_name"]} {form_data["last_name"]}\nEmail: {form_data["email"]}\nPhone number: {form_data["phone_number"]}\nMessage: {form_data["details"]}"""

            mail = None
            mail = Email(subject="Hey Sander, someone used the form on your website!", receiver="sander_pelgrims@outlook.com", body=message)
            mail.send()
            
            cards = db.execute("SELECT * FROM tools;")
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