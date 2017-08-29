import boto.ec2
import sys
import slack
import slack.chat
from slacker import Slacker

slack.api_token = 'Place_your_token_here'
slack.chat.post_message('#testbot', 'aws.py Initialized',username='python_bot')



auth = {"aws_access_key_id": "XXXXXXXXXX", "aws_secret_access_key": "XXXXXXXXXXXXXXXX"}

def main():
    # read arguments from the command line and 
    # check whether at least two elements were entered
    if len(sys.argv) < 3 :
	print "Usage: python aws.py {start|stop|reboot} INSTACNE_ID REGION\n"
	sys.exit(0)
    else:
	action = sys.argv[1] 

    if action == "start":
	startInstance()
    elif action == "stop":
    	stopInstance()
    elif action == "reboot":
         rebootInstance()
    else:
    	print "Usage: python aws.py {start|stop|reboot} INSTACNE_ID REGION \n"

##################################################
def startInstance():
    print "Starting the instance..."

    # change "eu-west-1" region if different
    try:
        ec2 = boto.ec2.connect_to_region(sys.argv[3], **auth)

    except Exception, e1:
        error1 = "Error1: %s" % str(e1)
        print(error1)
        sys.exit(0)

    # change instance ID appropriately  
    try:
         ec2.start_instances(instance_ids=sys.argv[2])
         slack.chat.post_message('#testbot','Instance -'+sys.argv[2]+' has been Started',username='python_bot')
    except Exception, e2:
        error2 = "Error2: %s" % str(e2)
        print(error2)
        sys.exit(0)

#####################################################
def stopInstance():
    print "Stopping the instance..."

    try:
        ec2 = boto.ec2.connect_to_region(sys.argv[3], **auth)

    except Exception, e1:
        error1 = "Error1: %s" % str(e1)
        print(error1)
        sys.exit(0)

    try:
         ec2.stop_instances(instance_ids=sys.argv[2])
         slack.chat.post_message('#testbot','Instance -'+sys.argv[2]+' has been Stopped',username='python_bot')

    except Exception, e2:
        error2 = "Error2: %s" % str(e2)
        print(error2)
        sys.exit(0)

######################################################
def rebootInstance():
    print "Restart the instance..."

    try:
        ec2 = boto.ec2.connect_to_region(sys.argv[3], **auth)

    except Exception, e1: 
        error1 = "Error1: %s" % str(e1)
        print(error1)
        sys.exit(0)

    try:
         ec2.reboot_instances(instance_ids=sys.argv[2])
         slack.chat.post_message('#testbot','Instance '+sys.argv[2]+' has been Rebooted',username='python_bot')
    except Exception, e2:
        error2 = "Error2: %s" % str(e2)
        print(error2)
        sys.exit(0)

if __name__ == '__main__':
    main()
