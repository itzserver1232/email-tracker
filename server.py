from flask import Flask, request, send_file, render_template_string, redirect, session, url_for
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

log_entries = []
PASSWORD = "297854"

@app.before_request
def auto_logout():
    if session.get("authenticated") and "login_time" in session:
        if datetime.now() - session["login_time"] > timedelta(minutes=1):
            session.pop("authenticated", None)
            session.pop("login_time", None)

@app.route("/pixel.png")
def pixel():
    user = request.args.get("user", "unknown")
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
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
            session["login_time"] = datetime.now()
            return redirect(url_for("view_log"))
        else:
            return "<h3>❌ Incorrect password</h3>"

    if not session.get("authenticated"):
        return '''
        <html><body>
        <h2>🔐 Enter Password to View Logs</h2>
        <form method="post">
            <input type="password" name="password" placeholder="Enter password" style="font-size:16px;" required>
            <input type="submit" value="Login" style="font-size:16px;">
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

    visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    html = '''
    <html>
    <head>
        <title>Email Tracker Logs</title>
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
        <br><form action="/logout" method="get"><button type="submit">🚪 Logout</button></form>
    </body>
    </html>
    '''
    return render_template_string(html, logs=logs, visitor_ip=visitor_ip)

@app.route("/logout")
def logout():
    session.pop("authenticated", None)
    session.pop("login_time", None)
    return redirect(url_for("view_log"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
