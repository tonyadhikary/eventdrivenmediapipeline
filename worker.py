import boto3
from PIL import Image
import os
import json
s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs', region_name='us-east-1')
