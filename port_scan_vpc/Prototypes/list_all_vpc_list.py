#!/usr/bin/python

import boto
import boto.ec2

fileCSV = open('/home/nsingh/Python_sniffer/SNIFF/vpc_hosts.conf','w+')

access_key = ''
secret_key = ''
region = 'ap-southeast-2'

#conn = boto.ec2_connect_to_region('ap-southeast-2', profile_name='default')
conn = boto.ec2.connect_to_region(region,aws_access_key_id=access_key,aws_secret_access_key=secret_key)

reservations = conn.get_all_instances(filters={'vpc_id':'vpc-d916a2bc'})
for reservation in reservations:
  for instances in reservation.instances:
    if instances.state == "running":
       name = instances.tags["Name"] if instances.tags["Name"] != "" else "unknown"
       print instances.private_ip_address,name
       fileCSV.write("%s %s\n"%(instances.private_ip_address,name))
