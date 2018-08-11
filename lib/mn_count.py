import requests


def get_cur_mn_count():
    mn_url = "https://stats.masternode.me/network-report/latest/json"

    mn_count = 0

    try:
        response = requests.request("GET", mn_url)

        if response.status_code is not 200:
            backup_mn_url = "https://insight.dashevo.org/insight-api-dash/masternodes/list"
            response = requests.get(backup_mn_url).json()

            for node in response:
                if node['status'] == "ENABLED":
                    mn_count += 1
                else:
                    continue
        else:
            network_stats = json.loads(response.text)['raw']
            mn_count = network_stats['mn_count_enabled']

    except Exception as e:
        print("Failed to get masternode count, trying on more time. \n{}".format(e))
        backup_mn_url = "https://insight.dashevo.org/insight-api-dash/masternodes/list"
        response = requests.get(backup_mn_url).json()

        for node in response:
            if node['status'] == "ENABLED":
                mn_count += 1

    return mn_count
