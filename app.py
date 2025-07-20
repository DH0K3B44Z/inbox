from flask import Flask, render_template, request
import threading
import os
import requests
import time
import random
from datetime import datetime

app = Flask(__name__, template_folder='templates')

running = False

def send_loop(tokens, messages, thread_id, prefix, delay):
    global running
    emojis = [" 3:)", " :)", " :3", " ^_^", " :D", " ;)", " :P", " ❤", " ☹"]
    msg_index = 0
    while running:
        for token in tokens:
            msg = f"{prefix} {messages[msg_index % len(messages)]} {random.choice(emojis)}"
            url = f"https://graph.facebook.com/v18.0/{thread_id}/messages"
            payload = {
                "messaging_type": "MESSAGE_TAG",
                "tag": "ACCOUNT_UPDATE",
                "recipient": f"{{\"thread_key\":\"{thread_id}\"}}",
                "message": msg,
                "access_token": token
            }
            try:
                r = requests.post(url, data=payload, timeout=10)
                now = datetime.now().strftime("%H:%M:%S")
                if r.ok:
                    print(f"\033[94m[{now}] Sent:\033[0m {msg}")
                else:
                    print(f"\033[91m[{now}] Failed:\033[0m {r.text}")
            except Exception as e:
                print(f"\033[91m[Error]\033[0m {str(e)}")
            time.sleep(delay)
        msg_index += 1

@app.route('/', methods=['GET', 'POST'])
def home():
    global running
    if request.method == 'POST':
        token_file = request.files['token_file']
        message_file = request.files['message_file']
        thread_id = request.form['thread_id']
        prefix = request.form['prefix']
        delay = int(request.form['delay'])

        tokens = [line.decode('utf-8').strip() for line in token_file.stream.readlines() if line.strip()]
        messages = [line.decode('utf-8').strip() for line in message_file.stream.readlines() if line.strip()]

        if not running:
            running = True
            t = threading.Thread(target=send_loop, args=(tokens, messages, thread_id, prefix, delay))
            t.daemon = True
            t.start()
        return "<h1 style='color:lime;'>✔ Message sending started! Check Termux console.</h1>"

    return render_template("index.html")

if __name__ == '__main__':
    os.system("clear")
    print("\033[92m[+] Server running on http://127.0.0.1:5000\033[0m")
    app.run(host='0.0.0.0', port=5000)
