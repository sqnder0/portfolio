import sqlite3
import smtplib, ssl
from dotenv import dotenv_values

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
    def __init__(self, text, receiver):
        self.receiver = receiver
        self.text = text
        
    def send(self):
        try:
            context = ssl.create_default_context()
            env = dotenv_values()
            password = env["password"]
            
            with smtplib.SMTP_SSL("smtp-mail.outlook.com", 465, context=context, timeout=10) as server:
                server.login("sander_pelgrims@outlook.com", password)
                server.sendmail(self.sender, self.receiver, self.text)
        except Exception as e:
            print(f"Failed to send email: {e}")