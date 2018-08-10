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

### Environmental Variables
* `DC_API_URL` (To fetch DashCentral Data)
* `AWS_ACCESS_ID` (For S3 Storage)
* `AWS_ACCESS_KEY` (For S3 storage)
* `S3_BUCKET` (For S3 Storage)
* `DISCORD TOKEN` (For the Discord Bot)

# Components

Right now we have a prototype of the webhook receiver that will eventually handle messages intended to be sent to Discord and Slack

We also have a prototype Discord Bot, and will soon be bringing over a Slack bot prototype.


## Discord Bot

Responds to the following commands
   
   `!GovHelp`
   
   `!Proposals`
   
   `!Cycle`
   

## Slack Bot

TBD


## Webhook Receiver

Right now it just prints stuff out anything that's submitted as a `POST` to bot.dashnexus.org/