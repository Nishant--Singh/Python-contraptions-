
import boto3
import slack
import slack.chat
import time
from slacker import Slacker

ACCESS_KEY = ""
SECRET_KEY = ""
slack.api_token =  ""
slack_channel = "#scanbot"


def call_rebooter(instance_id,event_type,description,availability_zone,region):
    slack.chat.post_message(slack_channel," *Instance :* " + instance_id + " *Event Type:* " + event_type + " *,* " + description + " * Availability Zone:* " + availability_zone + " *Region* " + region,username='AWS_Scheduled_Event_sniffer')
    ec2 = boto3.resource('ec2', region, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, )
    response = ec2.instances.filter(InstanceIds=[instance_id]).reboot()
    print "Instance is being rebooted"
    while all(i.state['Name'] != 'running' for i in ec2.instances.filter(InstanceIds=[instance_id])):
        print "Instance is being REBOOTED"
        time.sleep(5)
    else:
        print "Instance is *REBOOTED Successfully* and *Running*"
        slack.chat.post_message(slack_channel, str(instance_id) + "Instance is *REBOOTED Successfully* and *Running*",username='AWS_Scheduled_Event_sniffer')

##############################################################################################################################################################################

def call_maintenance(instance_id,event_type,description,availability_zone):
    slack.chat.post_message(slack_channel," *Instance :* " + instance_id + " *Event Type:* " + event_type + " *,* " + description + " * Availability Zone:* " + availability_zone + " *Region* " + region,username='AWS_Scheduled_Event_sniffer')
    slack.chat.post_message(slack_channel, "This is AWS Maintainece Event and this script won't take any action nor any human escalation is needed !",username='AWS_Scheduled_Event_sniffer')


##############################################################################################################################################################################

def call_pagerduty(instance_id,event_type,description,availability_zone,region):
    slack.chat.post_message(slack_channel," *Instance :* " + instance_id + " *Event Type:* " + event_type + " *,* " + description + " * Availability Zone:* " + availability_zone + " *Region* " + region,username='AWS_Scheduled_Event_sniffer')
    slack.chat.post_message(slack_channel, " *Please Note : THIS TYPE OF EVENT IS NOT BEING HANDLED BY THIS SCRIPT!! MAKE A JIRA ",username='AWS_Scheduled_Event_sniffer')


#---------------------------------------------------------------------------------------------------------------------------------------------------------#
def call_stop_starter(instance_id,event_type,description,availability_zone,region):
    slack.chat.post_message(slack_channel," *Instance :* " + instance_id + " *Event Type:* " + event_type + " *,* " + description + " * Availability Zone:* " + availability_zone +" *Region* "+ region,username='AWS_Scheduled_Event_sniffer')
    slack.chat.post_message(slack_channel,"The Script will now STOP and START the instance to get it back to Normal STATE" + instance_id ,username='AWS_Scheduled_Event_sniffer')

    ec2 = boto3.resource('ec2',region,aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, )
    response = ec2.instances.filter(InstanceIds=[instance_id]).stop()

    while all(i.state['Name'] != 'stopped' for i in ec2.instances.filter(InstanceIds=[instance_id])):
        print "Instance is still being Stopped"
        time.sleep(5)
    else:
        print "Instance are Stopped!!!"
        slack.chat.post_message(slack_channel,str(instance_id)+" is now in *STOPPED* State",username='AWS_Scheduled_Event_sniffer')

    slack.chat.post_message(slack_channel, str(instance_id) + " will now be STARTED in few seconds",username='AWS_Scheduled_Event_sniffer')

    start_response = ec2.instances.filter(InstanceIds=[instance_id]).start()

    while all(i.state['Name'] != 'running' for i in ec2.instances.filter(InstanceIds=[instance_id])):
        print "Instance is still being started"
        time.sleep(5)
    else:
        print "Instance are Up and running"
        slack.chat.post_message(slack_channel, str(instance_id) + " is now *UP and Running*",username='AWS_Scheduled_Event_sniffer')

#--------------------------------------------------------------------------------------------------------------------------------------------------------------#

def aws_event_resolver():
        regions = ['us-west-2', 'eu-central-1', 'ap-southeast-1','eu-west-1']

        for region in regions:

            client = boto3.client('ec2', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY,region_name=region, )
            instance_dict = client.describe_instance_status().get('InstanceStatuses')
            for inst in instance_dict:
                if inst.has_key('Events'):
                    print inst['InstanceId'],inst['Events'][0]['Code'],inst['Events'][0]['Description'],inst['AvailabilityZone']
                    instance_id = inst['InstanceId']
                    event_type = inst['Events'][0]['Code']
                    description = inst['Events'][0]['Description']
                    availability_zone = inst['AvailabilityZone']

                    if inst['Events'][0]['Code'] == "instance-reboot":
                        if "[Completed]" in inst['Events'][0]['Description']:
                            print "Nothing to do here"
                        else:
                            print "Calling Rebooter Now"
                            call_rebooter(instance_id,event_type,description,availability_zone,region)

                    elif inst['Events'][0]['Code'] == "system-reboot":
                        if "[Completed]" in inst['Events'][0]['Description']:
                            print "Nothing to do here"
                        else:
                            slack.chat.post_message(slack_channel, "*Instance :* " + inst['InstanceId'] + " *Event Type:* " + inst['Events'][0]['Code'] +  " No action required on your part the system reboot occurs during its scheduled maintenance window" + " *Found in :* " + inst['AvailabilityZone'] ,username='AWS_Scheduled_Event_sniffer')
                            ##call_rebooter(instance_id,event_type,description,availability_zone,region)

                    elif inst['Events'][0]['Code'] == "system-maintenance":
                        if "[Completed]" in inst['Events'][0]['Description']:
                            print "Nothing to do here"
                        else:
                            print "Calling Pagerduty maintainece"
                            call_maintenance(instance_id,event_type,description,availability_zone)

                    elif inst['Events'][0]['Code'] == "instance-retirement":
                        if "[Completed]" in inst['Events'][0]['Description']:
                            print "Nothing to do here"
                        else:
                            print "Calling Pagerduty maintainece"
                            call_pagerduty(instance_id,event_type,description,availability_zone)

                    elif inst ['Events'][0]['Code'] == "instance-stop":
                        if "[Completed]" in inst['Events'][0]['Description']:
                            print "Nothing to do here"
                        else:
                            print "Calling Stop and Go-Reboot"
                            print (instance_id)
                            call_stop_starter(instance_id,event_type,description,availability_zone,region)

                    #slack.chat.post_message(slack_channel," *Instance :* " + inst['InstanceId'] + " *Event Type:* " + inst['Events'][0]['Code'] + " *,* " +inst['Events'][0]['Description'] + " *Found in :* " + inst['AvailabilityZone'] ,username='AWS_Scheduled_Event_sniffer')

                    else:
                       print "This code part will never get executed"
                else:
                   pass #print ('No event found for {}'.format(inst['InstanceId']))
        return

aws_event_resolver()
