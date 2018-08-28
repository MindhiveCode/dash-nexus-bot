import requests
import seaborn as sns
from plotly import plotly as plty
import plotly.graph_objs as go
import pandas as pd
import os
import time
from lib.mn_count import get_cur_mn_count


nexus_hash = "7877338b947d7fe25d4dcc80979ee1f918736596677188ebadc79e5b9009d847"
nexus_hash_2 = "dc43dc408ddc7d7b7e064fda48aa0936be21d1ea67b538bf64ff6fdc6ecb550e"
kuva_hash = "ad48554075202678bfacb02c40c31529297a50d270965f18f1267dead22bd161"
dach_hash = "197ca53aa00d405992d4a4802d098732748a05839f0fd3d718035a66ebcb7a2a"


def get_votes(p_hash="2f09a8b36477c1f7be2b8e3153b32a67f8438172ae0b0fd6370ea00c6352a762"):
    print("Getting votes")
    query = "/governanceproposals/votes?testnet=0&proposalhash={}".format(p_hash)

    dn_base_url = os.environ.get("DN_API_URL")
    url = dn_base_url + query

    vote_response = requests.get(url)
    data = vote_response.json()['data']['governanceproposalvotes']

    for vote in data:
        if vote['VoteValue'] == "NO":
            vote['Math'] = -1
        if vote['VoteValue'] == "YES":
            vote['Math'] = 1

    print("Got votes")

    return data


def seaborn_graph(vote_data_df, p_data):
    # Just have to graph it now

    g = sns.relplot(x="Date", y="Cumulative Votes", kind="line", data=vote_data_df)
    # g = sns.relplot(x="Date", y="SMA", kind="line", title="Kuva" ,data=vote_data_df)

    g.fig.autofmt_xdate()
    g.fig.set_size_inches(w=6, h=3)

    try:
        g.savefig(fname="DACH.png")
        return True
    except Exception as e:
        print(e)
        return False


def plotly_graph(dataframe, proposal_info):

    # Create a trace
    trace = go.Scatter(
        x=dataframe['Date'],
        y=dataframe['Cumulative Votes'],
        mode="lines",
        line=dict(
            width=4
        )
    )

    data = [trace]

    # Edit the layout
    layout = dict(title=proposal_info['title'],
                  xaxis=dict(title='Date'),
                  yaxis=dict(title='Cumulative Votes'),
                  )

    fig = dict(data=data, layout=layout)

    plty.image.save_as(fig, filename="../images/Nexus.png", scale=2)

    return True


def convert_to_dataframe(vote_data_dict):
    df = pd.DataFrame.from_records(vote_data_dict)
    df['Date'] = pd.to_datetime(df['VoteTime'], origin='unix', unit='s')
    df.sort_values(by=['VoteTime'], ascending=True, inplace=True)
    df['Cumulative Votes'] = df.Math.cumsum()
    # df['SMA'] = df['Cumulative Votes'].rolling(window=5).mean
    # print(df.head())

    return df


if __name__ == "__main__":
    cur_hash = dach_hash

    # Get Proposal Data
    base_url = "https://www.dashcentral.org/api/v1"
    query = "/proposal?hash="
    proposal_data_url = base_url + query + cur_hash
    info_response = requests.get(proposal_data_url)
    proposal_info = info_response.json()['proposal']

    # Get Vote Data
    vote_data = get_votes(p_hash=cur_hash)
    vote_df = convert_to_dataframe(vote_data)

    # Graph
    graph = seaborn_graph(vote_df, proposal_info)
    # graph = plotly_graph(vote_df, proposal_info)
