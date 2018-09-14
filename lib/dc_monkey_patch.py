import requests
import json
import os
import sys
import time
import datetime
import functools
from lib.payments import *
from lib.useful_snippets import UsefulFunctions


def get_dc_data():
    dc_url = "https://www.dashcentral.org/api/v1/budget"
    budget_data = requests.get(dc_url)

    if budget_data.status_code == 200:
        proposals_dict = budget_data.json()
    else:
        print("No connection to Dash Central. Exiting...")
        sys.exit(1)

    return proposals_dict


def get_unique_proposal_data(p_hash=""):
    hash_key = "dc_p_" + p_hash
    if UsefulFunctions.check_cache(hash_key):
        print("Found Redis entry for {}".format(hash_key))
        return UsefulFunctions.read_cache(hash_key)
    else:
        dc_url = "https://www.dashcentral.org/api/v1/proposal?hash={}".format(p_hash)
        p_info = requests.get(dc_url).json()

        p_info = p_info['proposal']
        p_info.pop('description_base64_bb', None)
        p_info.pop('description_base64_html', None)
        p_info.pop('comments', None)

        UsefulFunctions.write_cache(p_info, hash_key, ex_time=3600)
        print("Wrote Redis entry for {}".format(hash_key))

        print(p_info)
        return p_info


def get_valid_list():
    insight_url = "https://insight.dashevo.org/insight-api-dash/gobject/list/proposal"
    valid_response = requests.get(insight_url)

    if valid_response.status_code == 200:
        valid_proposals = valid_response.json()
    else:
        print("No response from Insight API. Exiting...")
        sys.exit(1)

    return valid_proposals


def check_zombie_status(proposal_info):
    # Cache Zombie status every 24 hours
    hash_key = "ze_status_" + proposal_info['Hash']
    if UsefulFunctions.check_cache(hash_key):
        return UsefulFunctions.read_cache(hash_key)
    else:
        address = proposal_info['DataObject']['payment_address']
        amount = proposal_info['DataObject']['payment_amount']
        start_epoch = proposal_info['DataObject']['start_epoch']
        end_epoch = proposal_info['DataObject']['end_epoch']

        # Get last 2 superblock heights
        sb_1_height = check_governance_info()['result']['lastsuperblock']
        sb_2_height = int(sb_1_height) - 16616

        # Pull payment info for the previous two superblocks
        sb_1_data = get_cb_tx_for_sb(sb_1_height)
        sb_2_data = get_cb_tx_for_sb(sb_2_height)

        # If proposal hasn't be around long enough to be consider a zombie, then it can't be one
        if start_epoch > sb_2_data['time']:
            zombie_status = False
            return zombie_status

        # Check for payment in the most recent superblock and if we find one, set zombie = False
        for vout in sb_1_data['vout']:
            if address in vout['scriptPubKey']['addresses']:
                # Found a payment to this address in there, definitely not a zombie
                zombie_status = False
                return zombie_status
            else:
                continue

        # Check for payment in the superblock before that one and if we find one, set zombie = False
        for vout in sb_2_data['vout']:
            if address in vout['scriptPubKey']['addresses']:
                # Found a payment to this address in there, definitely not a zombie
                zombie_status = False
                return zombie_status
            else:
                continue

        # If we don't find a payment in the previous two superblocks, we're assuming it's a zombie
        zombie_status = True

        UsefulFunctions.write_cache(zombie_status, hash_key, ex_time=86400)

    return zombie_status


@functools.lru_cache(maxsize=1)
def check_governance_info():
    insight_url = "https://insight.dashevo.org/insight-api-dash/gobject/info"
    governance_response = requests.get(insight_url)

    if governance_response.status_code == 200:
        governance_info = governance_response.json()
    else:
        print("No response from Insight API. Exiting...")
        sys.exit(1)

    return governance_info


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
        block_height = check_governance_info()['result']['nextsuperblock']

    block_diff = block_height - cur_block

    predicted_block_time = int((block_diff * 2.625 * 60) + cur_blocktime)

    return predicted_block_time


def get_superblock_history():
    month_s = 2592000
    api_base_url = "https://api.dashintel.org"
    api_url = api_base_url + "/mvdash_budget_period_breakdown?period_end=lt.{}".format(int(time.time()) - (2 * month_s))

    sb_data = requests.get(api_url)

    if sb_data.status_code == 200:
        sb_data = sb_data.json()
    else:
        print("No response for Superblock Data... Exiting.")
        sys.exit(1)

    return sb_data


def combine(dc_data, valid_list):
    # Declare DC time string format
    time_string = "%Y-%m-%d %X"

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
    for proposal in dc_data['proposals']:
        end_time = datetime.datetime.strptime(proposal['date_end'], format(time_string))
        end_timestamp = end_time.timestamp()
        if end_timestamp > sb_time:
            final_data.append(proposal)
        else:
            continue

    # Generate new dictionary for of key/value pairs rather than list for valid proposal list
    kv_valid = dict()
    for proposal in valid_list:
        kv_valid[proposal["Hash"]] = proposal

    # Check Superblock payments
    cur_blockheight = get_network_status()['info']['blocks']
    for proposal in dc_data['proposals']:
        print("Checking payments")
        # start_epoch = datetime.datetime.strptime(proposal['date_added'], format=time_string).timestamp()
        # end_epoch = datetime.datetime.strptime(proposal['date_end'], format=time_string).timestamp()
        amount = kv_valid[proposal['hash']]['DataObject']['payment_amount']
        address = kv_valid[proposal['hash']]['DataObject']['payment_address']
        start_epoch = kv_valid[proposal['hash']]['DataObject']['start_epoch']
        end_epoch = kv_valid[proposal['hash']]['DataObject']['end_epoch']

        # Add necessary fields
        proposal.update({
            "start_epoch": start_epoch,
            "end_epoch": end_epoch,
            "payment_address": address,
            "payment_amount": amount
        })

        # Calculate payments

        proposal.update({"superblock_payments": gen_funding_array(proposal, cur_blockheight)})

    # Mark zombie proposals
    # If proposal has more than two payments total but hasn't received one in the past two superblocks, mark as zombie
    for proposal in final_data:
        print("Checking Zombie status")
        if proposal['total_payment_count'] > 2:
            zombie_status = check_zombie_status(kv_valid[proposal['hash']])
            proposal.update({"isZombie": zombie_status})
        else:
            zombie_status = False
            proposal.update({"isZombie": zombie_status})


    print("Fetched all missing data... Returning.")

    # Combine and prepare final dict
    dc_data['proposals'] = final_data

    return dc_data


def get_api_data():
    return combine(get_dc_data(), get_valid_list())


if __name__ == "__main__":
    combine(get_dc_data(), get_valid_list())
    # predict_block_time(get_network_status())
