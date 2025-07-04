from flask import Flask, send_file, request, render_template_string
from datetime import datetime

app = Flask(__name__)

@app.route("/pixel.png")
def pixel():
    user = request.args.get("user", "unknown")
    ip = request.remote_addr
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open("log.txt", "a") as f:
        f.write(f"[{time}] Opened by: {user} | IP: {ip}\n")
    
    return send_file("pixel.png", mimetype="image/png")

@app.route("/")
def home():
    return "Email Tracker Running"
    
@app.route("/log")
def view_log():
    try:
        with open("log.txt", "r") as f:
            lines = f.readlines()
    except:
        lines = []

    logs = []
    for line in reversed(lines[-100:]):
        parts = line.strip().split("] Opened by: ")
        if len(parts) == 2:
            time = parts[0].replace("[", "")
            user, ip = parts[1].split(" | IP: ")
            logs.append({"time": time, "user": user, "ip": ip})

    html = '''
    <html>
    <head>
        <title>Email Tracker Logs</title>
        <style>
            body { font-family: Arial; background: #f8f8f8; padding: 20px; }
            .log { background: white; margin: 10px 0; padding: 10px; border-left: 5px solid #007bff; }
            h2 { color: #007bff; }
        </style>
    </head>
    <body>
        <h2>📊 Email Open Log</h2>
        {% for entry in logs %}
            <div class="log">
                <strong>📧 {{ entry.user }}</strong><br>
                🕒 {{ entry.time }}<br>
                🌐 IP: {{ entry.ip }}
            </div>
        {% endfor %}
    </body>
    </html>
    '''
    return render_template_string(html, logs=logs)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
