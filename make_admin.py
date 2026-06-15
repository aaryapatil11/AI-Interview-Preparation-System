import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

email = "aaryapatil011@gmail.com"

cursor.execute(
    "UPDATE users SET role = 'admin' WHERE email = ?",
    (email,)
)

conn.commit()
conn.close()

print("Admin updated successfully")