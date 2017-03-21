#!/usr/bin/env python3

import slacker
import argparse
import datetime

# Needs to be an admin user token, bot doesn't work
slack_token = ""

parser = argparse.ArgumentParser(description = 'Manage Slack user activity')
parser.add_argument('-l', '--list-activity', action = 'store_true', 
                    help = 'print a list of user activity')
parser.add_argument('-r', '--remove-users', action = 'store_true', 
                    help = 'remove all inactive users from all public channels')
args = parser.parse_args()

if not slack_token:
    print('You need to set the slack_token variable, see the readme file')
    exit()

if not args.list_activity and not args.remove_users:
    parser.print_help()
    exit()

# Gather Data
slack = slacker.Slacker(token=slack_token) 
response = slack.users.list()
users = response.body['members']
response = slack.channels.list()
channels = response.body['channels']

user_report = {}
for user in users:
    if user['is_bot']:
        continue
    if user['deleted']:
        continue
    user_report[user['id']] = { 'name': user['name'],
                                'time': 0 }
    
for channel in channels:
    response = slack.channels.history(channel['id'])
    messages = response.body['messages']

    while response.body['has_more']:
        print("Retrieving more messages for {}...".format(channel['id']))
        response = slack.channels.history(channel=channel['id'], oldest=messages[99]['ts'])
        messages = messages + response.body['messages']

    for message in messages:
        if message['type'] == "message" and not "subtype" in message:
            if float(message['ts']) > float(user_report[message['user']]['time']):
                user_report[message['user']]['time'] = message['ts']

# Print report for -l
if args.list_activity:
    for uid, data in user_report.items():
        if data['time'] == 0:
            print("{},never".format(data['name']))
        else:
            delta = datetime.datetime.today() - datetime.datetime.fromtimestamp(float(data['time']))
            print("{},{}".format(data['name'], delta.days))

# Removal, -r
if args.remove_users:
    for channel in channels:
        channel_id = slack.channels.get_channel_id(channel)
        for uid, data in user_report.items():
            if data['time'] == 0:
                try:
                    slack.channels.kick(channel=channel_id,user=user_id)
                except not_in_channel:
                    pass
