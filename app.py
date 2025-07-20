from flask import Flask, render_template, request
import requests, time, threading, os

app = Flask(__name__)

def send_convo_message(token, thread_id, message):
    url = f"https://graph.facebook.com/v20.0/t_{thread_id}/messages"
    headers = {
        "Authorization": f"OAuth {token}"
    }
    data = {
        "message": message
    }
    response = requests.post(url, headers=headers, data=data)
    print(f"[CONVO] {thread_id}: {response.text}")

def post_comment(token, post_id, message):
    url = f"https://graph.facebook.com/v20.0/{post_id}/comments"
    headers = {
        "Authorization": f"OAuth {token}"
    }
    data = {
        "message": message
    }
    response = requests.post(url, headers=headers, data=data)
    print(f"[POST] {post_id}: {response.text}")

def start_sending(tokens, messages, target_id, delay, mode, hatersname=None):
    index = 0
    while True:
        token = tokens[index % len(tokens)].strip()
        message = messages[index % len(messages)].strip()

        if hatersname:
            message = f"{hatersname} {message}"

        if mode == "convo":
            send_convo_message(token, target_id, message)
        elif mode == "post":
            post_comment(token, target_id, message)

        index += 1
        time.sleep(delay)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        mode = request.form.get("mode")  # convo or post
        delay = int(request.form.get("delay", 5))
        target_id = request.form.get("target_id")
        hatersname = request.form.get("hatersname", "")

        # Read tokens
        tokens_file = request.files["tokens_file"]
        tokens = tokens_file.read().decode("utf-8").splitlines()

        # Read messages
        messages_file = request.files["messages_file"]
        messages = messages_file.read().decode("utf-8").splitlines()

        # Background thread
        thread = threading.Thread(
            target=start_sending,
            args=(tokens, messages, target_id, delay, mode, hatersname)
        )
        thread.start()

        return "✅ Started sending messages/comments in background."

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
