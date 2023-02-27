#!/usr/bin/python3

# Student: Grzegorz Piotrowski
# DevOps Assignment 1

from time import sleep
import boto3
import webbrowser
import subprocess
from time import time

keyPairFilename = "devopsAwsKey.pem"

userData = """#!/bin/bash
              yum update -y
              yum install httpd -y
              systemctl enable httpd
              systemctl start httpd
              touch /home/ec2-user/fileCommandsCompleted"""

ec2 = boto3.resource('ec2')

print("Creating a new ec2 instance...")

new_instances = ec2.create_instances(
    ImageId='ami-0aa7d40eeae50c9a9',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.nano',
    KeyName='devopsAwsKey',
    SecurityGroupIds=['sg-076cb4038b190be4e'],
    UserData=userData
)

instance = new_instances[0]
# Adding a name tag to the created instance
instance.create_tags(Tags=[{'Key':'Name', 'Value':'Web Server'}])

# Print out details of created instances
print("Created instances:")
for inst in new_instances:
    inst.reload()
    print("ID: " + inst.id + " Public IP: " + inst.public_ip_address)

instance.wait_until_running()
instance.reload()
print("Instance running")

# Checking if all UserData commands were executed and 'fileCommandsCompleted' file is on the EC2 instance
ssh_command = "ssh -o StrictHostKeyChecking=no -i " + keyPairFilename + " ec2-user@" + instance.public_ip_address + " 'ls'"
for i in range(10):
    result = subprocess.run(ssh_command, shell=True, stdout=subprocess.PIPE)
    filesList = result.stdout.decode('utf-8').strip().split('\n')
    print("Checking if Apache server is running...")
    if ("fileCommandsCompleted" in filesList):
        print("Apache server installed and running on " + instance.public_ip_address)
        break
    sleep(10)

# Opening the Apache test page in the browser
webbrowser.open_new_tab('http://' + instance.public_ip_address)


# Creating S3 bucket
s3 = boto3.resource('s3')
bucketName = "devops-lab-" + str(int(time() * 10000))

try:
    response = s3.create_bucket(Bucket=bucketName)
    print(response)
except Exception as error:
    print(error)

website_configuration = {
    'ErrorDocument': {'Key': 'error.html'},
    'IndexDocument': {'Suffix': 'index.html'}
}

bucket_website = s3.BucketWebsite(bucketName)

response = bucket_website.put(WebsiteConfiguration=website_configuration)

print("Bucket '" + bucketName + "' created.")
print("Upload an index.html file and test it works!")