import requests
import json
import tinys3
import boto
from boto.s3.key import Key
import os
import pdb

# bucket = 'dash-nexus-bot'
bucket = 'nexus-test-bucket-hodges'

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
# AWS_ACCESS_KEY_ID = "AKIAIRJCC6I7KVKA7QWA"
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
# AWS_SECRET_KEY = "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"

DC_API_URL = os.environ.get('DC_API_URL')


def get_new():
    response = requests.get(DC_API_URL)

    if response.status_code == 200:
        budget_dict = response.json()
    else:
        return {}

    return budget_dict


def get_old():
    conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)

    try:
        bucket_con = conn.get_bucket(bucket)
        print("Got bucket")
        key = bucket_con.get_key('latest.json')
        print("Got key")
        data = json.loads(key.get_contents_as_string('latest.json'))
        print("Downloaded data")
        return data

    except Exception as e:
        print(e)
        data = get_new()
        upload_new(data)
        return data


def get_both():
    new = get_new()
    old = get_old()

    return new, old


def parse_hashes(budget_dict):
    prop_hashes = set()

    # Add hashes to set
    for proposal in budget_dict['proposals']:
        prop_hashes.add(proposal['hash'])

    return prop_hashes


def upload_new(budget_data):
    conn = tinys3.Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)
    print('S3 Client Initiated')

    # f = bytes(json.dumps(budget_data))

    if os.name == 'nt':
        with open("latest.json", 'w') as json_dumper:
            json.dump(budget_data, json_dumper)

        with open("latest.json", 'rb') as to_upload:
            try:
                conn.upload('latest.json', to_upload, bucket=bucket)
                return True
            except Exception as e:
                print("Failure: {}".format(e))
                return False

    else:
        with open("tmp/latest.json", 'w') as json_dumper:
            json.dump(budget_data, json_dumper)

        with open("tmp/latest.json", 'rb') as to_upload:
            try:
                conn.upload('latest.json', f, bucket=bucket)
                return True
            except Exception as e:
                print("Failure: {}".format(e))
                return False


def check_for_new():
    new, old = get_both()
    new_hashes = parse_hashes(new)
    old_hashes = parse_hashes(old)

    diff = list(set(new_hashes) - set(old_hashes))

    if len(diff) > 0:
        print("Send message")

        # Iterate over proposals, print (mock doing something) for the newly added proposals.
        for proposal in new['proposals']:
            if proposal['hash'] in diff:
                print(proposal)

        if upload_new(new):
            print("Successfully uploaded file.")
        else:
            print("Failed to cache latest proposal data.")
    else:
        print("No new proposals. Waiting a bit.")


if __name__ == "__main__":
    check_for_new()
