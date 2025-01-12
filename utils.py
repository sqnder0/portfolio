import sqlite3

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