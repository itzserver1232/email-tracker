from flask import Flask, request, send_file, render_template_string, redirect, session, url_for
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Needed for login sessions

log_entries = []  # Store tracking info in memory
PASSWORD = "297854"  # Change this to your own password

@app.route("/pixel.png")
def pixel():
    user = request.args.get("user", "unknown")
    ip = request.remote_addr
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entries.append(f"[{time}] Opened by: {user} | IP: {ip}")
    return send_file("pixel.png", mimetype="image/png")

@app.route("/", methods=["GET"])
def home():
    return "📡 Email Tracking Server Running"

@app.route("/log", methods=["GET", "POST"])
def view_log():
    if request.method == "POST":
        if request.form.get("password") == PASSWORD:
            session["authenticated"] = True
            return redirect(url_for("view_log"))
        else:
            return "<h3>❌ Incorrect password</h3>"

    if not session.get("authenticated"):
        return '''
        <html><body>
        <h2>🔐 Enter Password to View Logs</h2>
        <form method="post">
            <input type="password" name="password" placeholder="Enter password">
            <input type="submit" value="Login">
        </form>
        </body></html>
        '''

    # Show logs
    logs = []
    for line in reversed(log_entries[-100:]):
        parts = line.strip().split("] Opened by: ")
        if len(parts) == 2:
            time = parts[0].replace("[", "")
            user, ip = parts[1].split(" | IP: ")
            logs.append({"time": time, "user": user, "ip": ip})

    visitor_ip = request.remote_addr  # Show current viewer's IP

    html = '''
    <html>
    <head>
        <title>📊 Email Tracker Logs</title>
        <style>
            body { font-family: Arial; background: #f5f5f5; padding: 20px; }
            .log { background: white; margin: 10px 0; padding: 10px; border-left: 5px solid #007bff; }
            h2 { color: #007bff; }
            .ip { font-size: 14px; color: #666; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h2>📊 Email Open Log</h2>
        <div class="ip">🔎 You are viewing from IP: <b>{{ visitor_ip }}</b></div>
        {% for entry in logs %}
            <div class="log">
                <strong>📧 {{ entry.user }}</strong><br>
                🕒 {{ entry.time }}<br>
                🌐 IP: {{ entry.ip }}
            </div>
        {% endfor %}
        <br><form method="post"><button type="submit" name="logout" value="1">🚪 Logout</button></form>
    </body>
    </html>
    '''
    return render_template_string(html, logs=logs, visitor_ip=visitor_ip)

# Optional: Log out by reloading /log with logout button
@app.route("/logout", methods=["GET"])
def logout():
    session.pop("authenticated", None)
    return redirect(url_for("view_log"))

if __name__ == "__main__":
    app.run(debug=True)
