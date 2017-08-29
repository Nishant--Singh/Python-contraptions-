import sys
import boto
from boto import ec2
import slack
import slack.chat
from slacker import Slacker

slack.api_token= ""
connection=ec2.connect_to_region("ap-southeast-2")
sg=connection.get_all_security_groups()

 
def getTag(instanceId):
 
    reservations=connection.get_all_instances(filters={'instance_id':instanceId})
    for res in reservations:
        for instance in res.instances:
            return instance.tags['Name'],instance.private_ip_address,instance.region
 
try:
 
    for securityGroup in sg:
       for rule in securityGroup.rules:
           global instanceId;
           if rule.to_port == '22'  and '0.0.0.0/0' in str(rule.grants):
                for instanceid in securityGroup.instances():
                   instanceId=str(instanceid)
                   print "Port 22 is open for 0.0.0.0/0:, SecurityGroupName: %s  Instance Details --> : %s " %(securityGroup.name,  getTag(instanceId.split(':')[1]))                   
                   slack.chat.post_message('#scanbot','>*Port* *22* *open* *for* *0.0.0.0/0* *in* `Security Group:` '+str(securityGroup.name)+'  `Instance Details:` '+'```'+str(getTag(instanceId.split(':')[1]))+'```',username='AWS_security_group_scanner')
                   slack.chat.post_message('#scanbot','*-----------------------------------------------------------------*',username='AWS_security_group_scanner')
except :
    print 'Some Error occurred : '
    print sys.exc_info()
