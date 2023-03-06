#!/usr/bin/python3

# Student: Grzegorz Piotrowski
# DevOps Assignment 1


import boto3
import webbrowser
import subprocess
import random
import string
import sys
from os.path import exists
from time import sleep


def createInstance(keyName, imageId, userData):
    ec2 = boto3.resource('ec2')
    print("Creating a new ec2 instance...")

    new_instances = ec2.create_instances(
        ImageId=imageId,
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.nano',
        KeyName=keyName,
        SecurityGroupIds=['sg-076cb4038b190be4e'],
        UserData=userData
    )

    instance = new_instances[0]
    # Adding a name tag to the created instance
    instance.create_tags(Tags=[{'Key':'Name', 'Value':'Web Server'}])

    # Print out details of the created instance
    while(instance.public_ip_address is None):
        sleep(1)
        print("Waiting to acquire the IP address...")
        instance.reload()
    print("Created instance ID: " + instance.id + ", Public IP: " + instance.public_ip_address)

    instance.wait_until_running()
    instance.reload()
    print(f"Instance {instance.id} is running.")

    # Checking if all UserData commands were executed and 'fileCommandsCompleted' file is on the EC2 instance
    ssh_command = "ssh -o StrictHostKeyChecking=no -i " + keyName + ".pem ec2-user@" + instance.public_ip_address + " 'ls'"
    for i in range(10):
        result = subprocess.run(ssh_command, shell=True, stdout=subprocess.PIPE)
        filesList = result.stdout.decode('utf-8').strip().split('\n')
        print("Checking if Apache server is running...")
        if ("fileCommandsCompleted" in filesList):
            print("Apache server installed and running at " + instance.public_ip_address)
            break
        sleep(10)

    return instance


def createBucket():
    s3 = boto3.resource('s3')
    print("Creating a new S3 Bucket...")
    alphaNum = string.ascii_lowercase + string.digits
    bucketName = "jbloggs-" + "".join(random.sample(alphaNum, 6))

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
    print("S3 Bucket '" + bucketName + "' created.")

    return s3.Bucket(bucketName)


if __name__ == "__main__":
    keyName = "devopsAwsKey"
    imageId = 'ami-006dcf34c09e50022'
    try:
        keyName= sys.argv[1]
    except IndexError:
        pass # No argument found. Using default keyPair instead
    
    keyFilename = keyName + ".pem"
    if not exists(keyFilename):
        print(f"Key Pair file {keyName}.pem not found. Closing the program...")
        exit()

    try:
        imageId = sys.argv[2]
    except IndexError:
        pass

    userData = """#!/bin/bash
                #yum update -y
                yum install httpd -y
                systemctl enable httpd
                systemctl start httpd
                echo "This instance is AMI ID is:" > index.html
                curl http://169.254.169.254/latest/meta-data/ami-id >> index.html
                echo "<hr>The instance ID is: " >> index.html
                curl http://169.254.169.254/latest/meta-data/instance-id >> index.html
                echo "<hr>The instance type is: " >> index.html
                curl http://169.254.169.254/latest/meta-data/instance-type >> index.html
                mv index.html /var/www/html
                touch /home/ec2-user/fileCommandsCompleted"""

    # Creating EC2 instance
    instance = createInstance(keyName, imageId, userData)

    # Opening the Apache test page in the browser
    webbrowser.open_new_tab('http://' + instance.public_ip_address)

    # Creating S3 bucket
    bucket = createBucket()

    # Download image using curl
    subprocess.run("curl -o logo.jpg http://devops.witdemo.net/logo.jpg", shell=True)

    s3Client = boto3.client("s3")

    # Upload image to S3 bucket and make it public
    s3Client.upload_file("logo.jpg", bucket.name, "logo.jpg", ExtraArgs={'ACL':'public-read', 'ContentType':'image/jpeg'})

    # Create index.html file with image in the S3 bucket
    with open("index.html", "w") as f:
        f.write(f'<html><body><img src="http://{bucket.name}.s3.amazonaws.com/logo.jpg"></body></html>')

    # Upload index.html to S3 bucket
    s3Client.upload_file("index.html", bucket.name, "index.html", ExtraArgs={'ACL':'public-read', 'ContentType':'text/html'})

    # Opening the S3 bucket website in the browser
    webbrowser.open_new_tab(f"http://{bucket.name}.s3-website-us-east-1.amazonaws.com")
    
    monitorCommands = f"""
        scp -i {keyFilename} monitor.sh ec2-user@{instance.public_ip_address}:.
        ssh -i {keyFilename} ec2-user@{instance.public_ip_address} 'chmod 700 monitor.sh'
        ssh -i {keyFilename} ec2-user@{instance.public_ip_address} './monitor.sh'
    """

    subprocess.run(monitorCommands, shell=True)

