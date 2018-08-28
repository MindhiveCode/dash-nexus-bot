from slackclient import SlackClient
import urllib
import json
import requests
import os
import logging


API_TOKEN = os.environ.get("SLACK_TOKEN")


rich_msg_json = {
    "text": "New Comment?",
    "attachments": [
        {
            "text": "Love this proposal!",
            "fallback": "Love this proposal....",
            "callback_id": "wopr_game",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "reply",
                    "text": "Reply?",
                    "type": "button",
                    "value": "True"
                },
                {
                    "name": "ignore",
                    "text": "Ignore",
                    "style": "danger",
                    "type": "button",
                    "value": "False",
                    "confirm": {
                        "title": "Are you sure?",
                        "text": "Are you sure you don't want to ignore it??",
                        "ok_text": "Yes",
                        "dismiss_text": "No"
                    }
                }
            ]
        }
    ]
}


# Build a fancy slack message, this could be tweaked to be an attachment with fancier formatting and inclusion of a custom thumbnail even
def build_message(**kwargs):  # Build message
    message = ("Put you fucking message here: {}".format(msg))
    return message


# Send a message directly to slack using the RTM API rather than using the bot integration
def send_msg(init_msg, rich_msg):  # This is what we'll link to from the encoder part - it processes input and sends the message
    sc = SlackClient(API_TOKEN)

    chan_id = init_msg

    try:
        sc.api_call(
            "chat.postMessage",
            channel=chan_id,
            text=built_message
        )
        logging.info('Sent msg to channel {}'.format(chan_id))
        return True
    except Exception as e:
        print('Failed to send message')
        print(e)
        return False


if __name__ == "__main__":
    send_msg()