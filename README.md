# AWS DevOps

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

## Resources
* Boto3 documentation \
https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

* Boto3 documentation - EC2 - Instance \
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#instance

* AWS documentation - EC2 - Metadata \
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html#imdsv1

* Boto3 - S3 \
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/bucket/index.html

* Boto3 - S3 - Uploading files \
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html

* Boto3 - EC2 - Client - Describe Images - to get the latest AMI ID
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/paginator/DescribeImages.html

* Boto 3: Resource vs Client \
https://www.learnaws.org/2021/02/24/boto3-resource-client/
