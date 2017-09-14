#!/usr/bin/env python

import requests
import pprint
import json
from requests.auth import HTTPBasicAuth
import socket

import slack
import slack.chat
from slacker import Slacker

slack.api_token =  ""
slack_channel = "#eenadu-siri-opennms"


def get_nodes_opennms():
    headers={'Accept': 'application/json' }
    x = requests.get('http://localhost:8980/opennms/rest/alarms?comparator=ge&severity=MINOR?limit=0',headers=headers , auth=('admin', 'Op3n%&^AD'))
    parsed = json.loads(x.content)
    #print json.dumps(parsed, indent=4, sort_keys=True)
    wriet_me_to_file = json.dumps(parsed, indent=4, sort_keys=True)
  #  f=open('out.txt', 'w')
    with open('out.txt','w') as f:
        f.write(wriet_me_to_file)
    for i in json.load(open('out.txt'))["alarm"]:
        try:
            print i["ipAddress"]
            slack.chat.post_message(slack_channel,"*Alert* *The* *Following* *IP* *just* *went* *down* -> "+i["ipAddress"],username='OpenNMS_BOT')
            print i["logMessage"]
            print i["lastEvent"]["serviceType"]["name"]
            slack.chat.post_message(slack_channel,"Service which was Impacted -> "+i["lastEvent"]["serviceType"]["name"],username='OpenNMS_BOT')
            slack.chat.post_message(slack_channel,i["logMessage"],username='OpenNMS_BOT')
            slack.chat.post_message(slack_channel,"___________________________________________________",username='OpenNMS_BOT')
        except Exception as e:
          print "something is wrong"
if __name__ == "__main__":
   x = get_nodes_opennms()
#   node_data = extract_nodes()
#   print node_data

