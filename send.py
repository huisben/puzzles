from flask import Flask, request, make_response, Response
import os
import json
import csv
import random
import urllib

from slackclient import SlackClient

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"] 

# Slack client for Web API requests
slack_client = SlackClient(SLACK_BOT_TOKEN)

# Flask webserver for incoming traffic from Slack
app = Flask(__name__)


puzzles = {}

with open('puzzles.csv', 'r') as f:
    reader = csv.reader(f)
    for k, v in reader:
        puzzles[k] = v

ogpuzzles = dict(puzzles)
puzzle = random.choice(list(puzzles.keys()))



def get_sol(key):
    global puzzles
    return puzzles.pop(key)

def make_attachment(text):

    attachments_json = [
        {
            "fallback": "wot mate",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "callback_id": "puzz1",
            "text": text,
            "actions": [
                {
                    "name": "finish",
                    "text": "Done!",
                    "type": "button",
                    "style": "primary",
                    "value": "finish",
                    "data_source": "external"
                },
                {
                    "name": "quit",
                    "text": "Give up",
                    "type": "button",
                    "style": "danger",
                    "value": "quit",
                    "data_source": "external"
                }
            ]
        }
    ]

    return attachments_json

def send_msg(channel, text, puzzle):
    slack_client.api_call(
      "chat.postMessage",
      channel=channel,  # "G6BRDQGE9",#"@ben"
      text=text,  #"Ready for today's puzzle?",
      attachments=make_attachment(puzzle)
    )

# send_msg("G6BRDQGE9", "Ready for today's puzzle?", puzzle)    

@app.route("/slack/new", methods=["POST"])
def new_puzzle():
    global puzzles
    global puzzle 

    if request.form['token'] == SLACK_VERIFICATION_TOKEN:

        print(request.form)
        puzzle = random.choice(list(puzzles.keys()))
        send_msg(request.form['channel_id'], "Here's a new puzzle!", puzzle)

    return make_response("", 200)



@app.route("/slack/message_actions", methods=["POST"])
def message_actions():
    global puzzles
    global puzzle

    # Parse the request payload
    form_json = json.loads(request.form["payload"])
    print(request.form)

    og_message = form_json["original_message"]["attachments"][0]["text"]
    print(og_message)
    og_message = urllib.parse.unquote(og_message[1:-1])
    print(og_message)
    
    if form_json['token'] == SLACK_VERIFICATION_TOKEN:
        # Check to see what the user's selection was and update the message
        selection = form_json["actions"][0]["value"]

        if selection == "finish":
            message_text = "Great job! Here's the solution anyway: " + get_sol(og_message)
        else:
            message_text = "Fail! Here's the solution: " + get_sol(og_message)

        response = slack_client.api_call(
          "chat.postMessage",
          channel=form_json["channel"]["id"],
          text=message_text,
          attachments=[]
        )

    return make_response("", 200)



if __name__ == "__main__":
    app.run()
