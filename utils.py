import sqlite3
import smtplib, ssl
from dotenv import dotenv_values
import wikipedia

class Database:
    def __init__(self, path):
        self.path = path

    def execute(self, command, *args):
        try:
            with sqlite3.connect(self.path) as conn:
                cur = conn.cursor()
                cur.execute(command, args)
                values = cur.fetchall()
                column_names = [description[0] for description in cur.description]
                
                rows = []
                for value_tuple in values:
                    row = {}
                    for index, value in enumerate(value_tuple):
                        row[column_names[index]] = value
                    rows.append(row)

                return rows
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

class Email:
     def __init__(self, text, sender, reciever):
        self.sender = sender
        self.reciever = reciever
        self.text = text
        
class Email:
    def __init__(self, subject, body, receiver):
        self.sender = "pelgrimssander17@gmail.com"
        self.receiver = receiver
        self.subject = subject
        self.body = body
        
        
    def send(self):
        try:    
                config = dotenv_values(".env")
                self.password = config.get("password")
                message = f"""from: <Sander>{self.sender}
To: {self.receiver}
Subject: {self.subject}\n
{self.body}
                """
                
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(self.sender, self.password)
                
                server.sendmail(self.sender, self.receiver, message)
                server.quit()
        except Exception as e:
            print(f"Failed to send email: {e}")

def get_cards():
    db = Database("portfolio.db")
    
    cards = db.execute("SELECT * FROM tools;")
    for card in cards:
        card["innerText"] = wikipedia.summary(card["wiki"], sentences=2)
    
    return cards