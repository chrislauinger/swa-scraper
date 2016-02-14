This is a spider for use with [Scrapy](http://www.scrapy.org) that crawls for and parses fares for one-way flights on Southwest's website and puts the fares in an AWS Dynamo DB

Setup after cloning repo on linux EC2 instance: 
sudo yum install git
sudo yum install emacs
sudo yum install make
sudo yum install libffi-devel
sudo yum install gcc
sudo yum install openssl-devel
sudo yum install -y gcc libxml2 libxml2-devel libxslt libxslt-devel
sudo pip install scrapy
sudo pip install boto3

copy aws credentials into /home/ec2-user/.aws/credentials

create privateConstants.py:
author =  ''
password = ''