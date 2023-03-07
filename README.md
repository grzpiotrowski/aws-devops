# AWS DevOps

The script creates a new EC2 Instance and an S3 Bucket in the default region.
Then an image is downloaded from a set URL and then uploaded and displayed on S3 website.

## Getting started

Install the AWS Command Line Interface:
```
sudo apt update
sudo apt install awscli
```

Configure your AWS credentials
```
mkdir ~/.aws
nano ~/.aws/credentials
```
Go to AWS Console and get the AWS CLI key and paste it into nano, then save the file and exit.

To complete the configuration, enter:
```
aws configure
```
to set the default region and output format:
```
AWS Access Key ID [****************QQHJ]: (leave unchanged)
AWS Secret Access Key [****************wWJ/]: (leave unchanged)
Default region name [None]: us-east-1
Default output format [None]: json
```

Install Boto3 Python module:
```
pip3 install boto3
```
or
```
python3 -m pip install boto3
```

## Running the script
The script takes in a few optional arguments:
* [1] - keyName: Key pair name (without the .pem extension)
* [2] - securityGroup: Name of the existing security group
* [3] - imageId: AMI (Amazon Machine Image) ID
* [4] - nameTag: EC2 Instance name

Example:
```
python3 devops1.py devopsAwsKey launch-wizard-1 ami-006dcf34c09e50022 "Test Web server"
```

Default values are used when the arguments are not provided.


## Resources
* Boto3 documentation \
https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

* Boto3 documentation - EC2 - Instance \
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#instance

* AWS documentation - EC2 - Metadata \
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html#imdsv1
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-categories.html

* Boto3 - S3 \
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/bucket/index.html

* Boto3 - S3 - Uploading files \
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html

* Boto3 - EC2 - Client - Describe Images - to get the latest AMI ID
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/paginator/DescribeImages.html

* Boto3 - Catching exceptions when using a resource client
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html#catching-exceptions-when-using-a-resource-client

* Boto 3: Resource vs Client \
https://www.learnaws.org/2021/02/24/boto3-resource-client/

* How to parse apache log files with Awk
https://luther.io/linux/how-to-parse-apache-log-files-with-awk/