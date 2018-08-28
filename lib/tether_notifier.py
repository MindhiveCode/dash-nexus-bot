import sendgrid
import os
import sys
import json
from sendgrid.helpers.mail import *

sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
# sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)


def check_cache(name):
    import redis
    db = redis.from_url(os.environ.get("REDIS_URL"))
    if db.get(name):
        print("Found cache data, continuing and then comparing against this.")
        return True
    else:
        return False


def write_cache(data, name):
    import redis
    db = redis.from_url(os.environ.get("REDIS_URL"))
    try:
        db.set(name, json.dumps(data))
        return True
    except Exception as e:
        print(e)
        print("Failed to write to cache")


def read_cache(filename):
    import redis

    db = redis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)
    data = json.loads(db.get(filename))

    return data


def poll_omni_explorer_address():
    import requests
    url = "https://api.omniexplorer.info/v1/address/addr/details/"

    payload = "addr=1NTMakcgVwQpMdGxRQnFKyb3G1FAJysSfz"
    headers = {
        'content-type': "application/x-www-form-urlencoded",
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Bad API response, exiting for now.")
        sys.exit(1)


def poll_omni_explorer_property():
    import requests
    url = "https://api.omniexplorer.info/v1/property/31"
    response = requests.request("GET", url)

    if response.status_code == 200:
        return response.json()
    else:
        print("Bad API response, exiting for now.")
        sys.exit(1)


def send_slack_message(amount, txid):
    import requests
    post_url = os.environ.get("SLACK_TETHER_WEBHOOK")

    amount_rnd = round(float(amount), 2)

    payload={"text": "{:,} Tether just moved. Check out the tx details <https://api.omniexplorer.info/v1/transaction/tx/{}|here!>".format(amount_rnd, txid),
                "username": "Tether Bot",
                "channel": "#news",
                "icon_url": "https://www.omniexplorer.info/c1a2b1ea01845d292661c605b31c0581.png"}

    print(payload)

    response = requests.post(post_url, json=payload)

    print(response)


def send_email(em_content):
    from_email = Email("tether@fakexchange.com")

    emails = ['jeff@mindhive.io', 'yuri@mindhive.io', 'bc@daim.io']

    for email in emails:
        to_email = Email(email)
        subject = "Tether movement deteched"
        content = Content("text/plain", em_content)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)


def check_for_movement():
    # Check for movement here

    new_data = poll_omni_explorer_property()

    # Check to make sure that we have cached data before continuing
    if check_cache('tether_data'):
        old_data = read_cache("tether_data")
    else:
        write_cache(new_data, "tether_data")
        old_data = read_cache("tether_data")

    # Calculate the difference between our old data and our new data
    movement = (float(new_data['totaltokens']) - (float(old_data['totaltokens'])))

    print(movement)

    new_grant = new_data['issuances'][0]
    amount = new_grant['grant']
    txid = new_grant['txid']

    if movement > 0 or movement < 0:
        content = """{} Tether moved from master address \n <a href="https://api.omniexplorer.info/v1/transaction/tx/{}">Block Explorer Link</a>""".format(amount, txid)
        # send_email(content)
        send_slack_message(amount, txid)
        # write_json(new_data, 'tether_data')
    else:
        print("No movement detected, sleeping for now.")
        sys.exit(1)
    print(response.status_code)


if __name__ == "__main__":
    check_for_movement()
