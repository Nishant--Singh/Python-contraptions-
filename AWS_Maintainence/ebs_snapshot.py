import boto3
import slack
import slack.chat
import time
import itertools
from slacker import Slacker

ACCESS_KEY = ""
SECRET_KEY = ""
slack.api_token = ""
slack_channel = "#my_test_channel"

def gather_info_ansible():
    regions = ['us-west-2', 'eu-central-1', 'ap-southeast-1']
    combined_list = []   # This needs to be returned
    for region in regions:
        instance_information = [] # I assume this is a list, not dict

        client = boto3.client('ec2', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY,
                              region_name=region, )
        instance_dict = client.describe_instances().get('Reservations')
        #print instance_dict
        for reservation in instance_dict:
            for instance in reservation['Instances']: # This is rather not obvious

                if instance[u'State'][u'Name'] == 'running' and instance.get(u'Tags') is not None:
                    ipaddress = instance[unicode('PrivateIpAddress')]
                    if "ansible" in instance[unicode('Tags')][0][unicode('Value')]:
                        tag = instance[unicode('Tags')][0][unicode('Value')]
                        zone = instance[unicode('Placement')][unicode('AvailabilityZone')]
                        volume_id = instance[unicode('BlockDeviceMappings')][0][unicode('Ebs')][unicode('VolumeId')]
                        info = ipaddress, tag, zone , volume_id
                        instance_information.append(info)
                    else:
                        pass
        combined_list.append(instance_information)
    return combined_list

def call_snapshot_creater(data):
    regions = ['us-west-2', 'eu-central-1', 'ap-southeast-1']

    for index,region in enumerate(regions):

        print "-----------------------------------------------------------"
      
        for ip_address,tags_descrip,regions_az,volume_id in data[index]:

           ec2 = boto3.resource('ec2', region, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, )
           print "Snapshot Creation For Ansible -> ",ip_address," initiated , tag = ", tags_descrip ,"region : ", regions_az
           slack.chat.post_message(slack_channel,"> ``` Snapshot Creation For Ansible Box -> "+ "" +str(tags_descrip)+ ""  +" IP ->"+str(ip_address)+ " INITIATED in region -> "+str(regions_az)+ "```" ,username='Ansible_box_snapshot_bot')
           time.sleep(1)
           print "Snapshot will be created with -> Name : ",tags_descrip
           slack.chat.post_message(slack_channel,"> Snapshot will be created with -> Name: "+ "*" +str(tags_descrip) +"*",username='Ansible_box_snapshot_bot')
           snapshot = ec2.create_snapshot(VolumeId=volume_id, Description=tags_descrip)
           tags = snapshot.create_tags(Tags=[{
            'Key': 'tag-value',
            'Value': tags_descrip
           },])
           print snapshot.id
           print "Snapshot is being created for Ansible box ", tags_descrip ,"with snapshot id :",snapshot.id
           slack.chat.post_message(slack_channel,"> Snapshot is being created for Ansible box "+str(tags_descrip)+" with snapshot id :"+ "*" +str(snapshot.id)+ "*",username='Ansible_box_snapshot_bot')
           #slack.chat.post_message(slack_channel,"Creating Snapshot for The volume"+ str(snapshot.id),username='Ansible_box_snapshot_bot')
           snapshot.load()
           while snapshot.state != 'completed':
                 print "The Snapshot :", snapshot.id , "for Ansible box named : ", tags_descrip  ,"is currently in :",snapshot.state," state"
                 time.sleep(40)
                 snapshot.load()
                 print snapshot.progress
           else:
                 print "Snapshot ",snapshot.id, "for Ansible box ", tags_descrip , "is now Ready!! Final state ->",snapshot.state
                 slack.chat.post_message(slack_channel,"> Snapshot "+snapshot.id+" for Ansible box ->"+tags_descrip+" is now *READY!!* Final state : "+"*"+snapshot.state+"*",username='Ansible_box_snapshot_bot') 

def call_snapshot_destroyer(data):
    regions = ['us-west-2', 'eu-central-1', 'ap-southeast-1']
    for index,region in enumerate(regions):
      for ip_address, tags_descrip, regions_az, volume_id in data[index]:
        client = boto3.client('ec2',region,aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        delete_snapshot = client.describe_snapshots(Filters=[{'Name': 'tag-value', 'Values':[tags_descrip]}])
        for snap in delete_snapshot['Snapshots']:
            if tags_descrip :
               print "Deleting snapshot %s , snapshot name %s" %(snap['SnapshotId'],tags_descrip)
               slack.chat.post_message(slack_channel,"> Deleting Previous Snapshot : "+snap['SnapshotId']+" Name :"+tags_descrip,username='Ansible_box_snapshot_bot')
               client.delete_snapshot(SnapshotId=snap['SnapshotId'])
            else:
                print "Nothing to delete !!"

if __name__ == '__main__':
    print "Calling Ansible Box Gather detail Method first!"
    ansible_box_info = gather_info_ansible()

    print "Now Calling the Destroyer of SNAPSHOT!! BEHOLD THIS IS HELL!!"
    call_snapshot_destroyer(ansible_box_info)

    #mapping = {i[0]: [i[1], i[2]] for i in data}
    print "Now Calling the Snapshot Creater!"
    call_snapshot_creater(ansible_box_info)    
