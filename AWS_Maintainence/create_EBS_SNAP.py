import boto3
import slack
import slack.chat
import time
from slacker import Slacker

ACCESS_KEY = ""
SECRET_KEY = ""
slack.api_token =  ""
slack_channel = "#scanbot"


def call_creater():
    regions = ['eu-central-1']
    for region in regions:
        ec2 = boto3.resource('ec2', region, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, )
        snapshot = ec2.create_snapshot(VolumeId='vol-f9e7d220', Description='fra01-he-trial-ansible01')
        print snapshot.id
#        slack.chat.post_message(slack_channel,"Creating Snapshot for The volume"+ str(snapshot.id),username='Ansible_box_snapshot_bot')

        get_all_snapshots = ec2.snapshots.filter(snap_id=['SnapshotIds'])
        print get_all_snapshots
        snapshot.load()
        print snapshot.progress
        while snapshot.state != 'completed':
              snapshot.load()
              print snapshot.progress
              print "Snapshot under creation"
              time.sleep(10)
              snapshot.load()
              print snapshot.progress
        else:
            print "snapshot READY"
#            slack.chat.post_message(slack_channel," For VolumeID blah snashot generated "+ str(snapshot.id),username='Ansible_box_snapshot_bot')


        ############################################################################################


if __name__ == '__main__':
    call_creater()
    
