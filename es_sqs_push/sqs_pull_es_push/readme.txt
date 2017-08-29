Run read_msg_n_upload_to_ES.py , it fill fetch messages from the SQS and then push to ES directly.
 - Currently crates a temporary file which has a hardcoded path, needs to be modified 
 - Also the Json needs to be parsed to remove any unwanted objects 
