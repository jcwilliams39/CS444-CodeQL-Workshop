"""CS 444 CodeQL demonstration application.

INTENTIONALLY INSECURE TRAINING CODE — DO NOT DEPLOY OR EXPOSE TO THE INTERNET.
Use only in a controlled class exercise, and fix findings before using it.
"""

import os
import pickle
import sqlite3
import subprocess
from flask import Flask, request, send_file

app = Flask(__name__)
DATABASE = "students.db"


@app.get("/student")
def student():
    """Example 1: SQL injection through string-built SQL."""
    student_name = request.args.get("name", "")
    connection = sqlite3.connect(DATABASE)
    query = "SELECT name, major FROM students WHERE name = '" + student_name + "'"
    rows = connection.execute(query).fetchall()
    connection.close()
    return {"students": rows}


@app.get("/ping")
def ping():
    """Example 2: command injection through shell=True."""
    host = request.args.get("host", "127.0.0.1")
    result = subprocess.check_output("ping -c 1 " + host, shell=True, text=True)
    return result


@app.get("/download")
def download():
    """Example 3: path traversal from untrusted filename."""
    filename = request.args.get("filename", "example.txt")
    path = os.path.join("uploads", filename)
    return send_file(path)


@app.post("/restore")
def restore():
    """Example 4: unsafe deserialization of untrusted request bytes."""
    data = request.get_data()
    restored = pickle.loads(data)
    return {"restored": str(restored)}


# Example 5: hardcoded secret for training only (not a real credential).
app.config["SECRET_KEY"] = "training-demo-secret-do-not-use-in-production"


if __name__ == "__main__":
    # Local development only; never expose this insecure app to a network.
    app.run(host="127.0.0.1", port=5000, debug=False)
