from flask import Flask, render_template_string, request
import threading, requests, time, random, os
from datetime import datetime

app = Flask(__name__)
running_convo = False
running_post = False

html_main = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Legend Server</title><style>
body{background:black;color:white;font-family:sans-serif;padding:50px;text-align:center;}
form{background:#111;padding:20px;border-radius:10px;display:inline-block;text-align:left;}
input,button{display:block;width:300px;margin:10px auto;padding:8px;border:none;border-radius:5px;}
button{background:cyan;color:black;font-weight:bold;}
h2{margin-top:40px;}
</style></head><body>
<h1>🔥 Legend Server</h1>
<h2>Convo Mode</h2>
<form method="POST" enctype="multipart/form-data" action="/start_convo">
 <input type="file" name="token_file" required>
 <input type="file" name="message_file" required>
 <input type="text" name="thread_id" placeholder="Thread ID" required>
 <input type="text" name="prefix" placeholder="Prefix (Hater's Name)" required>
 <input type="number" name="delay" placeholder="Delay (sec)" required>
 <button type="submit">Start Convo</button>
</form>
<h2>Post Mode</h2>
<form method="POST" enctype="multipart/form-data" action="/start_post">
 <input type="file" name="token_file" required>
 <input type="file" name="comment_file" required>
 <input type="text" name="post_id" placeholder="Post ID (e.g. 12345_6789)" required>
 <input type="number" name="delay" placeholder="Delay (sec)" required>
 <button type="submit">Start Post</button>
</form>
</body></html>
"""

def send_convo(tokens, messages, thread_id, prefix, delay):
    emojis = [" 😊", " 😉", " 😁", " ❤️"]
    idx = 0
    while running_convo:
        for tok in tokens:
            msg = f"{prefix} {messages[idx % len(messages)]}{random.choice(emojis)}"
            url = f"https://graph.facebook.com/v15.0/t_{thread_id}"
            resp = requests.post(url, data={"access_token": tok, "message": msg})
            now = datetime.now().strftime("%H:%M:%S")
            if resp.ok:
                print(f"[{now}] Convo → OK: {msg}")
            else:
                print(f"[{now}] Convo → ERROR: {resp.text}")
            time.sleep(delay)
        idx += 1

def send_post(tokens, comments, post_id, delay):
    emojis = [" 😊", " 😉", " 😁", " ❤️"]
    idx = 0
    while running_post:
        for tok in tokens:
            cm = comments[idx % len(comments)] + random.choice(emojis)
            url = f"https://graph.facebook.com/{post_id}/comments"
            resp = requests.post(url, data={"access_token": tok, "message": cm})
            now = datetime.now().strftime("%H:%M:%S")
            if resp.ok:
                print(f"[{now}] Post → OK: {cm}")
            else:
                print(f"[{now}] Post → ERROR: {resp.text}")
            time.sleep(delay)
        idx += 1

@app.route("/", methods=["GET"])
def home():
    return render_template_string(html_main)

@app.route("/start_convo", methods=["POST"])
def start_convo():
    global running_convo
    if running_convo:
        return "Convo already running!"
    tf = request.files["token_file"].read().decode().splitlines()
    mf = request.files["message_file"].read().decode().splitlines()
    thread_id = request.form["thread_id"]
    prefix = request.form["prefix"]
    delay = float(request.form["delay"])
    running_convo = True
    threading.Thread(target=send_convo, args=(tf, mf, thread_id, prefix, delay), daemon=True).start()
    return "<h2 style='color:lime'>✅ Convo started! Check console.</h2>"

@app.route("/start_post", methods=["POST"])
def start_post():
    global running_post
    if running_post:
        return "Post already running!"
    tf = request.files["token_file"].read().decode().splitlines()
    cf = request.files["comment_file"].read().decode().splitlines()
    post_id = request.form["post_id"]
    delay = float(request.form["delay"])
    running_post = True
    threading.Thread(target=send_post, args=(tf, cf, post_id, delay), daemon=True).start()
    return "<h2 style='color:lime'>✅ Post started! Check console.</h2>"

if __name__ == "__main__":
    os.system("clear")
    print("Server: http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000)
