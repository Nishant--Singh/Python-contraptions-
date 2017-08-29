import os
import json
import uuid
import time
import boto.sqs
import boto
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
from boto.sqs.message import RawMessage

sqs = boto.sqs.connect_to_region("ap-southeast-1",aws_access_key_id='XXXXX',aws_secret_access_key='XXXXXXXXXXX')
q = sqs.get_queue("Nishantqueue") #SQS queue name

#text_file = open('download.json', 'w')
m = q.read(visibility_timeout=15)
if m == None:
  print "No message!"
else:
  with open('download.json', 'w') as json_data:
    print m.get_body()
    json_data.write(m.get_body())

#    clean_data = json.load(json_data)  ## Working on removing the SSH Keys & other nom essential stuff  from Json 
#    for element in clean_data:         ## using  json parson
#      del element['sshdsakey'] 
#      json_data.write(clean_data) ## 

    json_data.close()
    q.delete_message(m)
    print "Push To ES"
    os.system('./push_to_ES.sh')
    print "Cleaning the temporary json file"
    os.remove('download.json')
    print "++++++ SUCCESSFUL RUN +++++++"
