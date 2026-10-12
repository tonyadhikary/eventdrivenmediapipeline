import boto3
from PIL import Image
import os
import json
s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs', region_name='us-east-1')

QUEUE_URL = 'YOUR_SQS_QUEUE_URL'  # Replace with SQS queue URL later
PROCESSED_BUCKET = 'YOUR_PROCESSED_BUCKET' # Replace with the name of the S3 bucket where processed images will be stored

def process_image(download_path, upload_path):
    with Image.open(download_path) as img:
        img = img.convert("L")  # Convert to grayscale
        img.save(upload_path)

def poll_queue():
    print("Listening for images in SQS")
    while True:
        response = sqs_client.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
        )

        if 'Messages' in response: 
            for message in response['Messages']: 
                body = json.loads(message['Body']) 
                if 'Records' in body:  
                    for record in body['Records']: 
                        source_bucket = record['s3']['bucket']['name'] 
                        object_key = record['s3']['object']['key'] 
                        file_name = os.path.basename(object_key)
                        download_path = f'/tmp/{file_name}'
                        upload_path = f'/tmp/processed_{file_name}'
                        print (f"Downloading {file_name} from bucket {source_bucket}")
                        s3_client.download_file(source_bucket, object_key, download_path)
                        print (f"Processing {file_name}")
                        process_image(download_path, upload_path)
                        print (f"Uploading processed {file_name} to bucket {PROCESSED_BUCKET}")
                        s3_client.upload_file(upload_path, PROCESSED_BUCKET, f'processed_{file_name}')
                        os.remove(download_path)
                        os.remove(upload_path)
                sqs_client.delete_message(
                    QueueUrl=QUEUE_URL,
                    ReceiptHandle=message['ReceiptHandle']
                ) 
                print("Message processed and deleted from SQS, waiting for next message")

if __name__ == "__main__":
    poll_queue()

#looks enough for now
#have to edit the queue url n bucket url 