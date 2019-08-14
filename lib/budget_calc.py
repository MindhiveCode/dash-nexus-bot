import json
import datetime
from pprint import pprint

SB_LENGTH = 16616 # Superblock cycle length
FPERIOD_LENGTH = 1616 # Finalization period length in blocks
REWARD_REDUCTION = 210240 # Every 576 * 365
SUBSIDY_REDUCTION = float(1/14) # Reduce by ~7.14%
BLOCK_TIME = int(60 * 2.625) # Convert to seconds

STARTING_BUDGET = float(7163.5306122449)
STARTING_BUDGET_PERIOD = 4
STARTING_FPERIOD_START = 1451835034
STARTING_SUPERBLOCK_HEIGHT = 398784
STARTING_SUPERBLOCK_TIMESTAMP = 1452096736


def add_budget_periods():
    """
    with open('budget_periods.json', 'r') as bp:
        initial_budget_periods = json.load(bp)
    """

    new_bps = list()
    last_reduction = 0
    reduction_count = 1

    for i in range(200):
        # Calculate budget
        if i - last_reduction == 14:
            # Trigger reward reduction
            if reduction_count == 1:
                new_budget = STARTING_BUDGET - (old_budget * SUBSIDY_REDUCTION)
            else:
                new_budget = old_budget - (old_budget * SUBSIDY_REDUCTION)
            last_reduction = i
            reduction_count += 1
        else:
            try:
                new_budget = new_budget
                old_budget = new_budget # Set old budget so we can subtract it later
            except:
                new_budget = STARTING_BUDGET
                old_budget = new_budget

        # Calculate superblock_height
        new_superblock_height = STARTING_SUPERBLOCK_HEIGHT + (SB_LENGTH * i)

        # Calculate superblock_timestamp
        new_superblock_timestamp = (i * SB_LENGTH * BLOCK_TIME) + STARTING_SUPERBLOCK_TIMESTAMP 

        # Calculate fperiodstart
        new_fperiodstart = (new_superblock_timestamp - (FPERIOD_LENGTH * BLOCK_TIME))

        new_sb = {
            'budget': new_budget,
            'budget_period': i + 4,
            'fperiodstart': new_fperiodstart,
            'superblock_height': new_superblock_height,
            'superblock_timestamp': new_superblock_timestamp
        }

        new_bps.append(new_sb)

    with open('budget_periods.json', 'w') as bp:
        json.dump(new_bps, bp)


def generate_budget_periods():
    base_block_number = 631408
    base_block_date = 1488744965
    dash_blocks_between_superblocks = 16616  # approx 30.29 days

    days_between_blocks = 30.29
    seconds_in_day = 86400
    seconds_between_blocks = days_between_blocks * seconds_in_day

    first_block_epoch = 1441622431 # First verified superblock - expected time between them
    fmt = "%y-%m-%d"
    budget_periods = 0
    cur_block_height = 332320  # Starts at the first superblock height
    time_since_first_budget_period = 0
    budget_period_dict_blocks = {}  # Initialize dict for block based budget periods
    budget_period_dict_timestamps = {}  # Initialize dict for timestamp based budget periods

    # The goal here is to create a dictionary of dates and block heights and then reference which one a given proposal
    # comes between

    while budget_periods <= 300:  # This will generate 5 years worth of proposals, starting with the first month
        time_since_first_budget_period += seconds_between_blocks
        cur_block_height += dash_blocks_between_superblocks
        budget_period_dict_timestamps[first_block_epoch+time_since_first_budget_period] = "Period {}".format(budget_periods)
        budget_periods += 1

    return budget_period_dict_timestamps



if __name__ == "__main__":
    add_budget_periods()
    # print(generate_budget_periods())