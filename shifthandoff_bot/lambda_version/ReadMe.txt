# This document describes how to modify slackbot_shifthandoff.py script to make it compatible with AWS lambda 
# How to create shifthandoff.zip file and how to configure lambda

Step 1.
Update the token id with a valid value.

Step 2.
Install python virtual environment and activate it.

Step 3.
Run slackbot_shifthandoff.py script in a virtual environment and install necessary python modules like 'requests' using pip.

Step 4.
Replace the main function with the lambda_handler function

if __name__ == "__main__": 
 should be changed to
def handler(event, context):

Step 5.
Change the location of the text file to "/tmp/handoff_text".
(As Lambda allows file reading/writing only in /tmp directory)

Step 6.
Zip this python script as per below command.
zip shifthandoff.zip slackbot_shifthandoff.py

Step 6.
Go to $virtualenv_directory/lib/python2.7/site-packages

Step 7.
Zip all packages in site-packages directory with below command
zip -r PATH_TO/shifthandoff.zip *

Step 8.
Upload this zip file in AWS Lambda.

Step 9.
Set the cron in Lambda as cron(32 11 ? * MON-FRI *)

Step 10.
Configure Handler value in AWS Lambda console as "slackbot_shifthandoff.handler"
