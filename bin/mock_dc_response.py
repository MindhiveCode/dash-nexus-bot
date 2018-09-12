import requests
import json
import os
import sys
import time
import datetime


def get_dc_data():
    dc_url = os.getenv("https://www.dashcentral.org/api/v1/budget")
    budget_data = requests.get(dc_url)

    if budget_data.status_code == 200:
        proposals_dict = budget_data.json()
    else:
        print("No connection to Dash Central. Exiting...")
        sys.exit(1)

    return proposals_dict


def get_valid_list():
    insight_url = os.getenv("https://insight.dashevo.org/insight-api-dash/gobject/list/valid")
    valid_response = requests.get(insight_url)

    if valid_response.status_code == 200:
        valid_proposals = valid_response.json()
    else:
        print("No response from Insight API. Exiting...")
        sys.exit(1)

    return valid_proposals


def check_superblock_data():
    insight_url = "https://insight.dashevo.org/insight-api-dash/gobject/info"
    network_response = requests.get(insight_url)

    if network_response.status_code == 200:
        network_info = network_response.json()
    else:
        print("No response from Insight API. Exiting...")
        sys.exit(1)

    return network_info


def get_network_status():
    insight_url = "https://insight.dashevo.org/insight-api-dash/status"
    blockchain_status = requests.get(insight_url)

    if blockchain_status.status_code == 200:
        blockchain_info = blockchain_status.json()
    else:
        print("No response from Insight API. Exiting...")
        sys.exit(1)

    return blockchain_info


def predict_sb_time(network_status=None, block_height=None):
    if network_status is None:
        network_status = get_network_status()

    cur_block = network_status['info']['blocks']
    cur_blocktime = int(time.time())

    if block_height is None:
        block_height = check_superblock_data()['result']['nextsuperblock']

    block_diff = block_height - cur_block

    predicted_block_time = int((block_diff * 2.625 * 60) + cur_blocktime)

    return predicted_block_time


def get_unique_proposal_data(p_hash=""):
    dc_url = "https://www.dashcentral.org/api/v1/proposal?hash={}".format(p_hash)
    p_info = requests.get(dc_url).json()

    p_info = p_info['proposal']
    p_info.pop('description_base64_bb', None)
    p_info.pop('description_base64_html', None)
    p_info.pop('comments', None)

    print(p_info)
    return p_info


def combine(dc_data, valid_list):
    # Generate list of proposal from DC
    dc_hashes = []
    for proposal in dc_data['proposals']:
        dc_hashes.append(proposal['hash'])

    # Generate list of actual proposals
    insight_hashes = []
    for proposal in valid_list:
        insight_hashes.append(proposal['Hash'])

    # Remove valid but basically expired proposals from /valid
    non_expired_hashes = []
    sb_time = predict_sb_time()
    print("Superblock Time = " + str(sb_time))
    for proposal in valid_list:  # Iterate through valid list
        print("Epoch end = " + str(proposal['DataObject']['end_epoch']))
        if proposal['DataObject']['end_epoch'] > sb_time:
            non_expired_hashes.append(proposal['Hash'])
        else:
            print(sb_time - proposal['DataObject']['end_epoch'])

    # Find the missing ones
    missing_hashes = list(set(non_expired_hashes) - set(dc_hashes))

    # Fetch data on missing ones and append
    for count, p_hash in enumerate(missing_hashes):
        print("Processing missing proposal {}/{}".format(count+1, len(missing_hashes)))
        dc_data['proposals'].append(get_unique_proposal_data(p_hash=p_hash))

    # Remove expired proposals from Dash Central data
    final_data = []
    time_string = "%Y-%m-%d %X"
    for proposal in dc_data['proposals']:
        end_time = datetime.datetime.strptime(proposal['date_end'], format(time_string))
        end_timestamp = end_time.timestamp()

        if end_timestamp > sb_time:
            final_data.append(proposal)
        else:
            continue

    print("Fetched all missing data... Returning.")

    # Combine and prepare final dict

    dc_data['proposals'] = final_data

    return dc_data


if __name__ == "__main__":
    combine(get_dc_data(), get_valid_list())
    # predict_block_time(get_network_status())
