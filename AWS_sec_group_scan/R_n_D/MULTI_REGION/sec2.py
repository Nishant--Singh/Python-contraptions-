import sys
import boto
from boto import ec2
import slack
import slack.chat
from slacker import Slacker

slack.api_token= ""
#regions = ['us-east-1','us-west-1','us-west-2','eu-west-1','sa-east-1','ap-southeast-1','ap-southeast-2','ap-northeast-1']
#sg = list()
#for region in regions:
#  connection=ec2.connect_to_region(region)
#  sg.extend(connection.get_all_security_groups())
 
def getTag(connection, instanceId): 
    reservations=connection.get_all_instances(filters={'instance_id':instanceId})
    for res in reservations:
        for instance in res.instances:
            return instance.tags['Name'],instance.private_ip_address,instance.region

regions = ['us-east-1','us-west-1','us-west-2','eu-west-1','sa-east-1','ap-southeast-1','ap-southeast-2','ap-northeast-1']

for region in regions:
    connection=ec2.connect_to_region(region)
    sg = connection.get_all_security_groups()
    try:
        for securityGroup in sg:
           for rule in securityGroup.rules:
               if rule.to_port == '22'  and '0.0.0.0/0' in str(rule.grants):
                   for instanceid in securityGroup.instances():
                       instanceId=str(instanceid)
                       print "Port 22 is open for 0.0.0.0/0:, SecurityGroupName: %s  Instance Details --> : %s " %(securityGroup.name,  getTag(connection, instanceId.split(':')[1]))
                   slack.chat.post_message('#scanbot','>*Port* *22* *open* *for* *0.0.0.0/0* *in* `Security Group:` '+str(securityGroup.name)+'  `Instance Details:` '+'```'+str(getTag(connection,instanceId.split(':')[1]))+'```',username='AWS_security_group_scanner')
                   slack.chat.post_message('#scanbot','*-----------------------------------------------------------------*',username='AWS_security_group_scanner')
    except :
        print 'Some Error occurred : '
        print sys.exc_info()
