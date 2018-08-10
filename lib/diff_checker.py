import requests
import json
import tinys3
import boto
import os
import pandas as pd

# bucket = 'dash-nexus-bot'
bucket = 'nexus-test-bucket-hodges'

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')

DC_API_URL = os.environ.get('DC_API_URL')


def get_new():
    budget_url = DC_API_URL + '/budget'
    response = requests.get(budget_url)

    if response.status_code == 200:
        budget_dict = response.json()
    else:
        return {}

    return budget_dict


def props_sorted():
    data = get_new()['proposals']

    for prop in data:
        abs_votes = prop['yes'] - prop['no']
        prop.update({"abs_votes": abs_votes})

    df = pd.DataFrame.from_dict(data)
    df.sort_values(by=['abs_votes'], inplace=True, ascending=False)

    sorted_data = df.to_dict(orient='records')

    return sorted_data


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


def get_old_2():
    try:
        response = requests.get("https://s3.us-east-2.amazonaws.com/nexus-test-bucket-hodges/latest.json")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("Error: {}".format(e))
        data = get_new()
        upload_new(data)
        return data


def get_both():
    new = get_new()
    old = get_old_2()

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
        with open("/tmp/latest.json", 'w') as json_dumper:
            json.dump(budget_data, json_dumper)

        with open("/tmp/latest.json", 'rb') as to_upload:
            try:
                conn.upload('latest.json', to_upload, bucket=bucket)
                return True
            except Exception as e:
                print("Failure: {}".format(e))
                return False


def check_for_new():
    print("Getting old data and fresh data")
    new, old = get_both()

    print("Generating list of proposal hashes from both")
    new_hashes = parse_hashes(new)
    old_hashes = parse_hashes(old)

    print("Generating diff list")
    diff = list(set(new_hashes) - set(old_hashes))

    if len(diff) > 0:
        print("New proposal detected")
        print("Sending message...")

        # Iterate over proposals, print (mock doing something) for the newly added proposals.
        for proposal in new['proposals']:
            if proposal['hash'] in diff:
                print(proposal)

        print("Uploading new data")
        if upload_new(new):
            print("Successfully uploaded file.")
        else:
            print("Failed to uploaded latest proposal data.")
    else:
        print("No new proposals. Waiting a bit.")


if __name__ == "__main__":
    # check_for_new()

    props_sorted()