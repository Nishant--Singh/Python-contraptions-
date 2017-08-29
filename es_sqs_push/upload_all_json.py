import json
import uuid
import time
import boto.sqs
import boto
import glob
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
from boto.sqs.message import RawMessage


def process_file(json_file):
	sqs = boto.sqs.connect_to_region("ap-southeast-1",aws_access_key_id='xxxxxxxxx',aws_secret_access_key='xxxxxxxxxxx')
	queue = sqs.get_queue("Nishantqueue")
	with open(json_file) as json_fileone:
            dataone=json_fileone.read()
            queue.write(queue.new_message(dataone))
            print "File sent successfully to queue"      	

json_files = glob.glob("blob.json")
for json_file in json_files:
    process_file(json_file)
