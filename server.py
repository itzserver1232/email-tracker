from flask import Flask, send_file, request
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

if __name__ == "__main__":
    app.run()
