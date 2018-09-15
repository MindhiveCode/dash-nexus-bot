import json
import requests
import time
import os
# import matplotlib.pyplot as plt
from datetime import datetime
from lib.useful_snippets import UsefulFunctions

# import s3_integration

vote_endpoint = ''
vote_cache = 'get_votes'

# Set this to be the change delta you want to trigger your notifications
delta_setting = int(os.getenv('DELTA_SETTING', 1))


def fetch_votes(proposal_hash='fb1d84dd8765ade8aa8cac8dadd96b27bf7223834b93edaf5ed08a5ec0d0d03f'):
    url = 'http://dash-stats.mindhive.io:5000/api/get_votes?proposal_hash={}'.format(proposal_hash)
    vote_data_raw = requests.request(method='GET', url=url).text
    vote_data_dict = json.loads(vote_data_raw)
    return vote_data_dict


def prepare_votes(vote_data):
    yes_count = 0
    no_count = 0
    abstain_count = 0

    new_preparation_y = []
    new_preparation_x = []

    yes_votes_over_time = []
    no_votes_over_time = []
    abstain_votes_over_time = []

    for vote in vote_data['votes']:
        if vote['outcome'] == 'yes':
            yes_count += 1
            yes_votes_over_time.append(yes_count)
            no_votes_over_time.append(no_count)
            abstain_votes_over_time.append(abstain_count)

        elif vote['outcome'] == 'no':
            no_count += 1
            no_votes_over_time.append(no_count)
            yes_votes_over_time.append(yes_count)
            abstain_votes_over_time.append(abstain_count)

        elif vote['outcome'] == 'abstain':
            abstain_count += 1
            abstain_votes_over_time.append(abstain_count)
            yes_votes_over_time.append(yes_count)
            no_votes_over_time.append(no_count)

        else:
            pass

        new_preparation_x.append(vote['ntime'])

    new_preparation_y.append((yes_votes_over_time, no_votes_over_time, abstain_votes_over_time))

    # votes_over_time = {'Yes':yes_votes_over_time, 'No': no_votes_over_time, 'Abstain': abstain_votes_over_time}

    data = (new_preparation_x, new_preparation_y, vote_data['hash'])

    return data


def graph(prepared_vote_data):
    # --- FORMAT 2</pre>

    proposal_hash = prepared_vote_data[2]

    x = sorted(prepared_vote_data[0])
    yes_votes = prepared_vote_data[1][0][0]
    no_votes = prepared_vote_data[1][0][1]
    abstain_votes = prepared_vote_data[1][0][2]

    # Basic stacked area chart.
    plt.figure(num=None, figsize=(10, 5), dpi=80, facecolor='w', edgecolor='k')

    plt.plot(x, yes_votes)
    plt.plot(x, no_votes)
    plt.plot(x, abstain_votes)

    plt.title("Votes Over Time")
    plt.ylabel("Yes Votes, No Votes, Abstain Votes")
    plt.xlabel('Time')

    plt.legend(['Yes Votes', 'No Votes', 'Abstain Votes'], loc='upper left')
    plt.gca().set_prop_cycle('color', ['g', 'r', 'y'])

    plt.tight_layout()
    plt.grid(alpha=0.3)

    graph_dir = 'tmp/graphs'

    if not os.path.exists(graph_dir):
        os.makedirs(graph_dir)

    # TODO Fix file-naming to be unique per day. It doesn't seem to overwrite in S3 right now.
    filename = str(proposal_hash) + '-' + '{}'.format(datetime.now().date()) + '.png'
    save_location = graph_dir + '/' + '{}'.format(filename)

    plt.savefig('{}'.format(save_location))

    return save_location, filename


def gen_chart():
    # Fetch Data - CHECK
    vote_data = fetch_votes()

    # Prepare Data - CHECK
    prepared_data = prepare_votes(vote_data)

    # Graph Data - CHECK
    graph_path, filename = graph(prepared_data)

    # Upload graph - IN PROGRESS
    url = s3_integration.add_and_upload_simple(graph_path, filename)

    # Return Link - IN PROGRESS
    return url


def get_mn_count():
    mn_url = "https://stats.masternode.me/network-report/latest/json"

    try:
        response = requests.request("GET", mn_url)

        if response.status_code is not 200:
            mn_count = 4700
        else:
            network_stats = json.loads(response.text)['formatted']
            mn_count = str(network_stats['f_mn_count']).replace(',', '')

    except:
        mn_count = 4700

    return mn_count


def poll_dash_central():
    proposal_hash = os.getenv('PROPOSAL_HASH')
    url = "https://www.dashcentral.org/api/v1/proposal?hash={}".format(proposal_hash)

    data = requests.get(url)
    proposal_data = json.loads(data.text)['proposal']

    min_quorum = int(get_mn_count())/10
    proposal_data['current_ratio'] = round((((proposal_data['yes']-proposal_data['no'])/min_quorum)*10), 2)

    return proposal_data


def webhook_message(message_data):
    # Set the webhook_url to the one provided by Slack when you
    # create the webhook at https://my.slack.com/services/new/incoming-webhook/
    webhook_url = os.getenv('SLACK_VOTES_WEBHOOK')

    # slack_data = {'text': message_data}
    slack_data = message_data

    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )

    return True


def gen_message_2(proposal_data):

    message = {
        "attachments":
        [
            {
                "fallback": "Title: {}: {}".format(proposal_data['title'], proposal_data['dw_url']),
                "text": "<{}|{}>".format(proposal_data['dw_url'],proposal_data['title']),
                "fields": [
                    {
                        "title": "Yes Votes",
                        "value": "{} (Δ{})".format(proposal_data['yes'], proposal_data['deltas']['yes_delta']),
                        "short": True
                    },
                    {
                        "title": "No Votes",
                        "value": "{} (Δ{})".format(proposal_data['no'], proposal_data['deltas']['no_delta']),
                        "short": True
                    },
                    {
                        "title": "Abstain Votes",
                        "value": "{}".format(proposal_data['abstain']),
                        "short": True
                    },
                    {
                        "title": "Votes Until Funding",
                        "value": "{}".format(proposal_data['remaining_yes_votes_until_funding']),
                        "short": True
                    },
                    {
                        "title": "Voting Deadline",
                        "value": "{}".format(proposal_data['voting_deadline_human']),
                        "short": True
                    },
                    {
                        "title": "Will Be Funded",
                        "value": "{}".format(proposal_data['in_next_budget']),
                        "short": True
                    }
                ],
                "color": "#2980b9"
            },
        ]
    }

    return message


def check_for_updates():
    new_data = poll_dash_central()

    # Check to make sure that we have cached data before continuing
    if UsefulFunctions.check_cache('dc_data'):
        old_data = UsefulFunctions.read_cache("dc_data")
    else:
        UsefulFunctions.write_cache(new_data, "dc_data")
        old_data = UsefulFunctions.read_cache("dc_data")

    yes_delta = 0
    no_delta = 0
    comment_delta = 0

    try:
        yes_delta = int(new_data['yes']) - int(old_data['yes'])
        no_delta = int(new_data['no']) - int(old_data['no'])
        comment_delta = int(new_data['comment_amount']) - int(old_data['comment_amount'])

    except Exception as e:
        print(e)

    deltas = {"yes_delta": yes_delta,
              "no_delta": no_delta,
              "comment_delta": comment_delta
              }

    new_data['deltas'] = deltas

    if yes_delta > delta_setting or no_delta > delta_setting:
        UsefulFunctions.write_cache(new_data, "dc_data")  # Update our persistent storage
        webhook_message(gen_message_2(new_data))  # Send message via Webhook
        print("Ran once, fired off update. Delta Y:{} N:{}".format(yes_delta, no_delta))
    else:
        print("Ran once. Waiting until next run to notify. Delta too small (Y:{} N:{})".format(yes_delta, no_delta))


if __name__ == "__main__":
    check_for_updates()