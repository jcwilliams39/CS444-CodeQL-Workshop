
"""CS 444 CodeQL demonstration application.

INTENTIONALLY INSECURE TRAINING CODE.
DO NOT RUN OR DEPLOY THIS APPLICATION.

This application contains five security examples
for testing GitHub CodeQL.
"""

import os
import pickle
import sqlite3
import subprocess

from flask import Flask, request, send_file

app = Flask(__name__)
DATABASE = "students.db"


# Example 1: SQL Injection
@app.get("/student")
def student():
    """Vulnerable SQL query using user input."""

    student_name = request.args.get("name", "")

    connection = sqlite3.connect(DATABASE)

    # Vulnerability: User input is added directly to SQL
    query = (
        "SELECT name, major FROM students WHERE name = '"
        + student_name
        + "'"
    )

    rows = connection.execute(query).fetchall()
    connection.close()

    return {"students": rows}


# Example 2: Command Injection
@app.get("/ping")
def ping():
    """Vulnerable command execution."""

    host = request.args.get("host", "127.0.0.1")

    # Vulnerability: Untrusted input is passed to shell
    result = subprocess.check_output(
        "ping -c 1 " + host,
        shell=True,
        text=True
    )

    return result


# Example 3: Path Traversal
@app.get("/download")
def download():
    """Vulnerable file download."""

    filename = request.args.get(
        "filename",
        "example.txt"
    )

    # Vulnerability: Filename is not validated
    path = os.path.join("uploads", filename)

    return send_file(path)


# Example 4: Unsafe Deserialization
@app.post("/restore")
def restore():
    """Vulnerable deserialization of user input."""

    data = request.get_data()

    # Vulnerability: Untrusted data is deserialized
    restored = pickle.loads(data)

    return {"restored": str(restored)}


# Example 5: Flask Debug Mode
if __name__ == "__main__":

    # Vulnerability: Debug mode is enabled
    # and the server listens on all interfaces
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
