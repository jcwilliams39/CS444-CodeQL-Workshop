
"""CS 444 CodeQL Demonstration Application.

The original five security issues have been fixed.

BONUS POINT ATTEMPT:
Issue 6 demonstrates insecure temporary file creation.

This version is intentionally vulnerable for CodeQL
testing only. Do not run or deploy it.
"""

import ipaddress
import sqlite3
import subprocess
import tempfile
from pathlib import Path

from flask import Flask, request, send_from_directory

app = Flask(__name__)

DATABASE = "students.db"
UPLOAD_FOLDER = Path(__file__).resolve().parent / "uploads"


# FIX 1: SQL Injection
@app.get("/student")
def student():
    """Use parameterized SQL queries."""

    student_name = request.args.get("name", "")

    connection = sqlite3.connect(DATABASE)

    # Prevent SQL injection with a parameterized query
    query = "SELECT name, major FROM students WHERE name = ?"

    rows = connection.execute(
        query, (student_name,)
    ).fetchall()

    connection.close()

    return {"students": rows}


# FIX 2: Command Injection
@app.get("/ping")
def ping():
    """Validate input and avoid shell commands."""

    host = request.args.get("host", "127.0.0.1")

    try:
        ip = ipaddress.ip_address(host)

        # Only allow loopback IP addresses
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


# FIX 3: Path Traversal
@app.get("/download")
def download():
    """Restrict file downloads to the uploads folder."""

    filename = request.args.get(
        "filename", "example.txt"
    )

    return send_from_directory(
        str(UPLOAD_FOLDER),
        filename
    )


# FIX 4: Unsafe Deserialization
@app.post("/restore")
def restore():
    """Use JSON instead of unsafe pickle loading."""

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error": "Expected JSON object"}, 400

    return {"restored": data}


# FIX 5: Flask Debug Mode
# Debug mode is disabled in the main application.


# ==========================================
# BONUS POINT ATTEMPT - SECURITY ISSUE #6
# ==========================================


# BONUS POINT ATTEMPT - Fix 6
# Secure temporary file creation

@app.get("/bonus-temp")
def bonus_temp():
    """Uses secure temporary file creation."""

    with tempfile.TemporaryFile(mode="w+t") as file:
        file.write("Temporary test data")

    return {"message": "Temporary file handled securely"}



# Main Application
if __name__ == "__main__":

    # Security fix: Debug mode disabled
    # Application only listens locally
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
