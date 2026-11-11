
"""CS 444 CodeQL demonstration application.

Updated version with security vulnerabilities fixed.
"""

import ipaddress
import json
import sqlite3
import subprocess
from pathlib import Path

from flask import Flask, request, send_from_directory

app = Flask(__name__)
DATABASE = "students.db"
UPLOAD_FOLDER = Path(__file__).resolve().parent / "uploads"


# Fix 1: SQL Injection
@app.get("/student")
def student():
    """Use parameterized SQL queries."""

    student_name = request.args.get("name", "")

    connection = sqlite3.connect(DATABASE)

    # User input is handled as a parameter
    query = "SELECT name, major FROM students WHERE name = ?"

    rows = connection.execute(
        query, (student_name,)
    ).fetchall()

    connection.close()

    return {"students": rows}


# Fix 2: Command Injection
@app.get("/ping")
def ping():
    """Validate input and avoid shell commands."""

    host = request.args.get("host", "127.0.0.1")

    try:
        ip = ipaddress.ip_address(host)

        # Only allow local IP addresses
        if not ip.is_loopback:
            return {"error": "Invalid host"}, 400

    except ValueError:
        return {"error": "Invalid IP address"}, 400

    result = subprocess.run(
        ["ping", "-c", "1", str(ip)],
        shell=False,
        capture_output=True,
        text=True,
        timeout=5,
        check=False
    )

    return result.stdout


# Fix 3: Path Traversal
@app.get("/download")
def download():
    """Restrict file downloads to the uploads folder."""

    filename = request.args.get(
        "filename", "example.txt"
    )

    # Only allow files within the uploads folder
    return send_from_directory(
        str(UPLOAD_FOLDER),
        filename
    )


# Fix 4: Unsafe Deserialization
@app.post("/restore")
def restore():
    """Use JSON instead of unsafe pickle loading."""

    try:
        data = request.get_json()

        if not isinstance(data, dict):
            return {"error": "Expected JSON object"}, 400

        return {"restored": data}

    except Exception:
        return {"error": "Invalid JSON data"}, 400


# Fix 5: Flask Debug Mode
if __name__ == "__main__":

    # Debug mode disabled
    # Only accessible from the local computer
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
