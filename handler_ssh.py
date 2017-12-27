import boto3
import time
import datetime
import paramiko
import os

def worker_handler(event, context):

    s3_client = boto3.client('s3')
    # ec = boto3.client('ec2')
    #Download private key file from secure S3 bucket
    s3_client.download_file('ggs-///////','key.pem','/tmp/key.pem')

    k = paramiko.RSAKey.from_private_key_file("/tmp/key.pem")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    host= '10.200.71.28'
    print "Connecting to " + host
    c.connect( hostname = host, username = "ec2-user", pkey = k )
    print "Connected to " + host

    commands = [
        "df -h"
        ]
    for command in commands:
        print "Executing {}".format(command)
        stdin , stdout, stderr = c.exec_command(command)
        print stdout.read()
        print stderr.read()

    return
    {
        'message' : "Script execution completed. See Cloudwatch logs for complete output"
    }

def lambda_handler(event, context):
    worker_handler()
    return 'successful'


if __name__ == '__main__':
    worker_handler([], [])
