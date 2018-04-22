import sys
import json

import requests
from flask import Flask, request, jsonify
import config

app = Flask(__name__)


@app.route("/status")
def server_status_handler():
    return jsonify({"success": True, "data": {"running": "ok"}})


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == config.FB_VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            if "messaging" not in entry:
                continue
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"][
                        "id"]  # the recipient's ID, which should be your page's facebook ID
                    if "text" not in messaging_event["message"]:
                        continue
                    message_text = str(messaging_event["message"]["text"])  # the message's text
                    if "play " in message_text:
                        song_name = message_text.replace("play ","")
                        send_message(sender_id, "received song request for " + song_name)
                        send_message(sender_id, send_bg_cmd_to_rapyuta(song_name))
                    else:
                        send_message(sender_id, "not supported action! :p do some more work")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):
    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": config.FB_PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


def send_bg_cmd_to_rapyuta(song_name):
    headers = {
        "Authorization": "Bearer " + config.RAPYUTA_TOKEN,
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "remote_update_log": "", "remote_update_script": "", "shell": "/bin/bash", "bg": True, "env": {},
        "runas": "root",
        "cmd": "(killall /usr/bin/omxplayer.bin ||  rm -rf songs_requested && ./bin/youtube_play %s)" % song_name,
        "device_ids": ["37a8764c-3b8f-4906-adb4-489bea65ff5e"],
        "cwd": ""
    })
    r = requests.post("https://api.apps.rapyuta.io/api/device-manager/v0/cmd/", headers=headers, data=data)
    return "running for you :)" if r.status_code == 200 else "some error with : " + r.status_code + r.text


if __name__ == '__main__':
    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=True)
