# Maintainer Nishant Singh

import requests
import json
import pprint
import datetime
import time


def get_channel_users(user_id):
    payload_user = {'token': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxxx', 'user': user_id}
    user_det = requests.post('https://slack.com/api/users.info', data=payload_user)
    json_user_loader = json.loads(user_det.text)
    # print json_user_loader['user']['name']

    return (json_user_loader['user']['name'])

def post_messages_to_slack():
    uploadfile = "nishant"  # Please input the filename with path that you want to upload.
    print "This is inside post to slack"
    with open(uploadfile, 'rb') as f:
        #print f
        param = {
               'token': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx',
               'channels': 'C1PJ17FFT',
               'title': 'Handoff'
                }
        r = requests.post(
                "https://slack.com/api/files.upload",
                params=param,
                files={'file': f}
               )
        print r.text
        print r.headers
        print r.status_code


def get_channel_messages():
    start_time_messages = datetime.datetime.today().replace(hour=10, minute=30, second=0, microsecond=0) ## 4:00:00 PM GST    
    ##TEST##start_time_messages =  datetime.datetime.today().replace(hour=5, minute=30, second=0, microsecond=0)
    epooch_oldest = time.mktime(start_time_messages.timetuple())
    stop_time_messages = datetime.datetime.today().replace(hour=11, minute=30, second=0, microsecond=0)  ## 5:00:00 PM
    ##TEST##stop_time_messages = datetime.datetime.today().replace(hour=6, minute=30, second=0, microsecond=0)
    epooch_newsest = time.mktime(stop_time_messages.timetuple())

    payload = {'token': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', 'channel': 'G03UNKYBG', 'latest':epooch_newsest  , 'oldest':epooch_oldest }
    r = requests.post('https://slack.com/api/groups.history', data=payload)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(r.json())  # Prints all channels
    # print r.json()

    print "========="
    json_objects = json.loads(r.text)
    #with open("nishant", "w") as f:
    file = open("nishant","w")
    for i in json_objects['messages']:
          user_id = i['user']
          return_names = get_channel_users(user_id)
          print return_names
          file.write(return_names+"\n")
          print i['text']
          file.write(""+i['text']+"\n")


if __name__ == "__main__":
    get_channel_messages()
    post_messages_to_slack()
