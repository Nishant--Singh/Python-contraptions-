# encoding: utf-8
import sys
import boto
from boto import ec2
import slack
import slack.chat
from slacker import Slacker
import unicodedata

from tabulate import tabulate #  pip install tabulate
slack.api_token= ""
#reload(sys)
#sys.setdefaultencoding("ascii")
 
def getTag(connection, instanceId): 
    reservations=connection.get_all_instances(filters={'instance_id':instanceId})
    for res in reservations:
      for instance in res.instances:
        if instance.state == "running":     
           return instance.tags['Name'],instance.private_ip_address,instance.region
        else:
           return None

#regions = ['us-east-1','us-west-1','us-west-2','eu-west-1','sa-east-1','ap-southeast-1','ap-southeast-2','ap-northeast-1']
#regions = ['us-west-2','eu-central-1','ap-southeast-1']  ##Prod VPC
regions = ['us-west-2']
data = []
header = ["Port","Open For","Security group","Instance Details"]

for region in regions:
    connection=ec2.connect_to_region(region)
    sg = connection.get_all_security_groups()
    try:
        for securityGroup in sg:
           for rule in securityGroup.rules:
               if '0.0.0.0/0' in str(rule.grants):
                  for instanceid in securityGroup.instances():
                      instanceId=str(instanceid)
               
                      tag = getTag(connection, instanceId.split(':')[1])
                      if tag is not None:
                        # tab =[str(rule.to_port),"0.0.0.0/0",str(securityGroup.name),str(getTag(connection, instanceId.split(':')[1]))]
                         tab  = [str(rule.to_port), "0.0.0.0/0", str(securityGroup.name), tuple(i.encode('UTF8') for i in getTag(connection, instanceId.split(':')[1])[0:2] )]
                        #  tab=[str(rule.to_port), "0.0.0.0/0", str(securityGroup.name), tuple(list(i.encode('UTF8') for i in getTag(connection, instanceId.split(':')[1])[0:2] ) + [getTag(connection, instanceId.split(':')[1])[2]])] 
                         data.append(tab)
    except Exception as e:
        pass

print (tabulate(data, headers=header, tablefmt='simple'))
cool_stuff = tabulate(data, headers=header, tablefmt='simple')
slack.chat.post_message('#smso-private','```Scan Report for PDX SAASOPS ```',username='AWS_security_group_scanner')
slack.chat.post_message('#smso-private','```'+cool_stuff+'```',username='AWS_security_group_scanner')
