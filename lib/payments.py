import requests
import sys
import json
from decimal import *
import os

from lib.useful_snippets import UsefulFunctions


# Caches Superblock TX data for each blockheight
def get_cb_tx_for_sb(blockheight):
    hash_key = "sb_data_" + str(blockheight)

    if UsefulFunctions.check_cache(hash_key):
        return UsefulFunctions.read_cache(hash_key)

    else:
        block_data_url = "https://insight.dash.org/insight-api-dash/block/{}".format(blockheight)
        block_tx_response = requests.get(block_data_url)

        if block_tx_response.status_code == 200:
            block_tx = block_tx_response.json()['tx']
        else:
            print("Bad response for Superblock TX list.")
            return None

        # Coinbase tx are always the first output in every block so we select the first entry listed
        cb_tx = block_tx[0]
        tx_data_url = "https://insight.dash.org/insight-api-dash/tx/{}".format(cb_tx)

        sb_tx_response = requests.get(tx_data_url)

        if sb_tx_response.status_code == 200:
            sb_tx_data = sb_tx_response.json()
        else:
            print("Bad response for Superblock TX payments")
            sys.exit(1)

        UsefulFunctions.write_cache(sb_tx_data, hash_key, ex_time=86400)

    return sb_tx_data


def calc_valid_sb(start_epoch, end_epoch):
    file_name = "budget_periods.json"
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    new_path = os.path.join(cur_dir, file_name)
    print(new_path)
    with open(new_path, 'r') as budget_period_json:
        sb_data = json.load(budget_period_json)

    b_height_array = list()

    for sb in sb_data:
        if start_epoch < sb['superblock_timestamp'] < end_epoch:
            b_height_array.append(sb['superblock_height'])

    print(b_height_array)

    if b_height_array == 0:
        return []
    else:
        return b_height_array


def check_matching_payment(address, amount, blockheight):
    amount = Decimal(amount).quantize(Decimal('.00000001'))  # Cast to the right decimal place

    tx_info = get_cb_tx_for_sb(blockheight)

    if tx_info is not None:  # If this block hasn't happened yet, we error out this way.
        for tx in tx_info['vout']:
            tx_value = Decimal(tx['value']).quantize(Decimal('.00000001'))
            tx_address = tx['scriptPubKey']['addresses'][0]  # Assuming it's the first entry in this list.

            if tx_value == amount:
                print("Matching tx amount")
                if tx_address == address:
                    return True

    return False


def gen_funding_array(proposal_data, cur_block):
    pay_hash_key = "payments_" + proposal_data['hash']

    if UsefulFunctions.check_cache(pay_hash_key):
        return UsefulFunctions.read_cache(pay_hash_key)

    else:
        start_epoch = proposal_data['start_epoch']
        end_epoch = proposal_data['end_epoch']
        address = proposal_data['payment_address']
        amount = proposal_data['payment_amount']

        valid_blockheights = calc_valid_sb(start_epoch, end_epoch)
        payment_dict = dict()

        for sb in valid_blockheights:
            if check_matching_payment(address, amount, sb):
                payment_dict.update({sb: "Paid"})
            elif sb > cur_block:
                payment_dict.update({sb: "Future"})
            else:
                payment_dict.update({sb: "Not Paid"})

        UsefulFunctions.write_cache(payment_dict, pay_hash_key, ex_time=259200)

    return payment_dict


if __name__ == "__main__":
    block_h = 947112 - 16616
    payment = 785.000
    check_matching_payment("XnNdk5s2JNPEVYB4brKmfFNuotoujWEuQd", payment, block_h)

