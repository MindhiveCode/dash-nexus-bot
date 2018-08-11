import requests
import json
import time


def update_post(interval):
    # pulling in posts from medium to refresh the content
    mediumURL = "https://medium.com/dashnexus?format=json"
    mediumData = json.loads(requests.get(mediumURL).text[16:])

    loopCounter = 0
    # mediumData
    for post in mediumData['payload']['references']['Post']:
        thisPost = mediumData['payload']['references']['Post'][post]

        if (loopCounter == 0):
            post1 = thisPost

        if (loopCounter == 1):
            post2 = thisPost

        if (loopCounter == 2):
            post3 = thisPost

        loopCounter = loopCounter + 1


def get_posts():
    # pulling in posts from medium
    mediumURL = "https://medium.com/dashnexus?format=json"
    mediumData = json.loads(requests.get(mediumURL).text[16:])

    loopCounter = 0
    # mediumData
    for post in mediumData['payload']['references']['Post']:
        thisPost = mediumData['payload']['references']['Post'][post]

        if (loopCounter == 0):
            post1 = thisPost

        if (loopCounter == 1):
            post2 = thisPost

        if (loopCounter == 2):
            post3 = thisPost

        loopCounter = loopCounter + 1

    return mediumData['payload']['references']['Post']


def parse_posts(data):
    parsed_data = {}

    counter = 0
    for key, post in data.items():
        if counter < 5:
            medium_base = "https://medium.com/dashnexus/"
            url = medium_base + post['uniqueSlug']

            # url = "https://medium.com/dashnexus/prototypes-iot-decentralized-governance-27c5ae35d464"
            parsed_data[post['id']] = {"title": post['title'], "url": url, "subtitle": post['content']['subtitle']}

            counter += 1
        else:
            continue

    # print(parsed_data)

    return parsed_data


if __name__ == "__main__":
    pass
