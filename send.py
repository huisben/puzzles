from flask import Flask, request, make_response, Response
import os
import json
import csv
import random

from slackclient import SlackClient

# Your app's Slack bot user token
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"] 

# Slack client for Web API requests
slack_client = SlackClient(SLACK_BOT_TOKEN)

# Flask webserver for incoming traffic from Slack
app = Flask(__name__)

# Post a message to a channel, asking users if they want to play a game

reader = csv.reader(open('puzzles.csv', 'r'))
puzzles = {}

for k, v in reader:
    puzzles[k] = v

puzzle = random.choice(list(puzzles.keys()))

attachments_json = [
    {
        "fallback": "wot mate",
        "color": "#3AA3E3",
        "attachment_type": "default",
        "callback_id": "menu_options_2319",
        "text": puzzle,
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


print(slack_client.api_call(
  "chat.postMessage",
  channel="G6BRDQGE9",
  text="Ready for today's puzzle?",
  attachments=attachments_json
))


@app.route("/slack/message_options", methods=["POST"])
# def message_options():
#     # Parse the request payload
#     form_json = json.loads(request.form["payload"])

#     # menu_options = {
#     #     "options": [
#     #         {
#     #             "text": "Chess",
#     #             "value": "chess"
#     #         },
#     #         {
#     #             "text": "Global Thermonuclear War",
#     #             "value": "war"
#     #         }
#     #     ]
#     # }

#     return Response(json.dumps(menu_options), mimetype='application/json')


@app.route("/slack/message_actions", methods=["POST"])
def message_actions():
    global puzzles
    global puzzle
    # Parse the request payload
    form_json = json.loads(request.form["payload"])

    # Check to see what the user's selection was and update the message
    selection = form_json["actions"][0]["value"]

    if selection == "finish":
        message_text = "Great job! Here's the solution anyway: " + puzzles[puzzle]
        
    else:
        message_text = "Fail! Here's the solution: " + puzzles[puzzle]
    
    puzzle = puzzles.pop(puzzle)
    puzzle = random.choice(list(puzzles.keys()))

    response = slack_client.api_call(
      "chat.postMessage",
      channel=form_json["channel"]["id"],
      ts=form_json["message_ts"],
      text=message_text,
      attachments=[]
    )

    if selection == "finish":
        print(slack_client.api_call(
          "chat.postMessage",
          channel="G6BRDQGE9",
          text="Here's another one!",
          attachments=attachments_json
        ))

    return make_response("", 200)



if __name__ == "__main__":
    app.run()
