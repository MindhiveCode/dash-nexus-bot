# NexusBot

Version 1.1


## Setup

This system runs great on Heroku using 2x Dynos for the different process types. We also use Heroku Scheduler to run scheduled tasks to see if a new proposals has been added to the Governance system.

We use a `web` process to receive webhooks from external services and run a `worker` process for each bot.


### Requirements

* Python 3
* requests
* pandas
* flask
* tinys3
* boto
* discord
* pandas
* sendgrid
* plotly
* redis

### Environmental Variables
* `DC_API_URL` (To fetch DashCentral Data)
* `AWS_ACCESS_ID` (For S3 Storage)
* `AWS_ACCESS_KEY` (For S3 storage)
* `S3_BUCKET` (For S3 Storage)
* `DISCORD TOKEN` (For the Discord Bot)
* `REDIS_URL` (For the persistent data store to do diffs)
* `SENDGRID_API_KEY` (For the tether messages)
* `PROPOSAL_HASH` (For the vote_watcher)
* `ENVIRONMENT` (PRODUCTION/DEVELOPMENT)
* `SLACK_VOTES_WEBHOOK` (The webhook URL for Slack that sends vote updates to the #dashcentral channel)
* `SLACK_TETHER_WEBHOOK` (The webhook URL to for Slack that sends messages to the #news channel)
* `DELTA_SETTING` (The delta required to trigger an event in regards to vote changes on DC)


# Components

Right now we have a prototype of the webhook receiver that will eventually handle messages intended to be sent to Discord and Slack

We also have a prototype Discord Bot, and will soon be bringing over a Slack bot prototype.

We now have two scheduled tasks (using Heroku Scheduler) that run every 10 minutes to check for any changes to the proposal vote count, and to check if any new Tether have been created.

The Tether bot sends a slack notification and sends an e-mail from mailto:tether@fakexchange.com

## Discord Bot

* Replies to `!Proposals` with a list of all currently active proposals and their vote counts.
* Replies to `!Cycle `with the latest countdown information regarding the voting cycle.
* Replies to `!News` with the latest blog posts on our Medium blog
* Replies to `!Nexus` with a list of possible commands
   
   
## Slack Bot

TBD


## Webhook Receiver

Right now it just prints stuff out anything that's submitted as a `POST` to bot.dashnexus.org/