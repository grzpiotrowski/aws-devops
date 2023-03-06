#!/usr/bin/python3

# Student: Grzegorz Piotrowski
# DevOps Assignment 1

"""
    The script takes in a few optional arguments:
    [1] - keyName: Key pair name (without the .pem extension)
    [2] - securityGroup: Name of the existing security group
    [3] - imageId: AMI (Amazon Machine Image) ID

    Example:
    python3 devops1.py devopsAwsKey launch-wizard-1 ami-006dcf34c09e50022

    Default values are used when the arguments are not provided.
"""

import boto3
import botocore
import webbrowser
import subprocess
import random
import string
import sys
from os.path import exists
from time import sleep, time


def createInstance(keyName, securityGroup, imageId, userData, nameTag, timeout=60):
    """Creates a new t2.nano EC2 instance."""

    ec2 = boto3.resource('ec2')
    print("Creating a new ec2 instance...")

    new_instances = ec2.create_instances(
        ImageId=imageId,
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.nano',
        KeyName=keyName,
        SecurityGroups=[securityGroup],
        UserData=userData
    )

    instance = new_instances[0]
    # Adding a name tag to the created instance
    instance.create_tags(Tags=[{'Key':'Name', 'Value':nameTag}])

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
    startTime = time()
    while time() < startTime+timeout:
        # Every 10 secs check if the file indicating all userData commands executed exists
        result = subprocess.run(ssh_command, shell=True, stdout=subprocess.PIPE)
        filesList = result.stdout.decode('utf-8').strip().split('\n')
        print("Checking if Apache server is running...")
        if ("fileCommandsCompleted" in filesList):
            print("Apache server installed and running at " + instance.public_ip_address)
            break
        sleep(10)

    return instance


def createBucket():
    """Creates a new S3 bucket."""

    s3 = boto3.resource('s3')
    print("Creating a new S3 Bucket...")
    alphaNum = string.ascii_lowercase + string.digits
    bucketName = "jbloggs" + "".join(random.sample(alphaNum, 6))

    try:
        s3.create_bucket(Bucket=bucketName)
    except s3.meta.client.exceptions.BucketAlreadyExists as error:
        print("Bucket already exists. Creating a bucket with another name...")
        bucketName = "jbloggs" + "".join(random.sample(alphaNum, 6))
        s3.create_bucket(Bucket=bucketName)
    except Exception as error:
        print(error)
        print("Could not create a new S3 bucket. Exiting the script...")
        exit()
    print("S3 Bucket '" + bucketName + "' created.")

    return s3.Bucket(bucketName)


def configureBucketWebsite(bucket, imageName):
    """Configures a sample S3 bucket website with an image"""

    s3 = boto3.resource('s3')

    website_configuration = {
        'ErrorDocument': {'Key': 'error.html'},
        'IndexDocument': {'Suffix': 'index.html'}
    }

    bucket_website = s3.BucketWebsite(bucket.name)
    bucket_website.put(WebsiteConfiguration=website_configuration)

    s3Client = boto3.client("s3")

    # Upload image to S3 bucket and make it public
    s3Client.upload_file(imageName, bucket.name, imageName, ExtraArgs={'ACL':'public-read', 'ContentType':'image/jpeg'})

    # Create index.html file with image in the S3 bucket
    with open("index.html", "w") as f:
        f.write(f'<html><body><img src="http://{bucket.name}.s3.amazonaws.com/{imageName}"></body></html>')

    # Upload index.html to S3 bucket
    s3Client.upload_file("index.html", bucket.name, "index.html", ExtraArgs={'ACL':'public-read', 'ContentType':'text/html'})




if __name__ == "__main__":
    # Default parameters
    keyName = "devopsAwsKey"
    securityGroup = "launch-wizard-1"
    imageId = "ami-006dcf34c09e50022"
    nameTag = "Test Web Server"


    # Check if the first optional argument was passed
    try:
        keyName= sys.argv[1]
    except IndexError:
        pass # No argument found. Using default keyPair instead (key pair name)
    
    # Check if key file exists
    keyFilename = keyName + ".pem"
    if not exists(keyFilename):
        print(f"Key Pair file {keyName}.pem not found. Closing the program...")
        exit()

    # Check if the second optional argument was passed (Security group name)
    try:
        securityGroup = sys.argv[2]
    except IndexError:
        pass

    # Check if the third optional argument was passed (AMI ID)
    try:
        imageId = sys.argv[3]
    except IndexError:
        pass

    # Check if the fourth optional argument was passed (Name Tag)
    try:
        nameTag = sys.argv[4]
    except IndexError:
        pass

    # Commands to be executed when the instance is launched
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
                echo "<hr>Availability zone: " >> index.html
                curl http://169.254.169.254/latest/meta-data/placement/availability-zone >> index.html
                mv index.html /var/www/html
                touch /home/ec2-user/fileCommandsCompleted"""

    # Creating EC2 instance
    instance = createInstance(keyName, securityGroup, imageId, userData, nameTag, timeout=60)

    # Opening the Apache test page in the browser
    webbrowser.open_new_tab('http://' + instance.public_ip_address)

    # Creating S3 bucket
    bucket = createBucket()

    # Download image using curl
    subprocess.run("curl -o logo.jpg http://devops.witdemo.net/logo.jpg", shell=True)

    # Configure a sample S3 bucket website with an image
    configureBucketWebsite(bucket, "logo.jpg")

    # Opening the S3 bucket website in the browser
    webbrowser.open_new_tab(f"http://{bucket.name}.s3-website-us-east-1.amazonaws.com")

    # Writing EC2 and S3 website URLs to a file
    file = open("grzegorzpiotrowskiurls.txt", "w")
    file.write(f"http://{bucket.name}.s3-website-us-east-1.amazonaws.com" +
               "\n" + 
               f"http://{instance.public_ip_address}")
    file.close()
    
    # Upload and run monitoring script on EC2 instance
    monitorCommands = f"""
        scp -i {keyFilename} monitor.sh ec2-user@{instance.public_ip_address}:.
        ssh -i {keyFilename} ec2-user@{instance.public_ip_address} 'chmod 700 monitor.sh'
        ssh -i {keyFilename} ec2-user@{instance.public_ip_address} './monitor.sh'
    """
    print("*** MONITORING METRICS ***")
    subprocess.run(monitorCommands, shell=True)
    print(26*"*")
    print("EC2 instance and S3 bucket website launched successfully!")

