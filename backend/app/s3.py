import boto3
# s3.py 

from app.config import S3_KEY, S3_SECRET

s3 = boto3.client('s3', aws_access_key_id=S3_KEY, 
                  aws_secret_access_key=S3_SECRET)


def upload_file(file, bucket, key):
    s3.upload_file(file, bucket, key)

def download_file(bucket, key):
    s3.download_file(bucket, key, key)

# other helpers