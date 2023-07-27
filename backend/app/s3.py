# s3.py

import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError
from app.config import S3_KEY, S3_SECRET
from fastapi import HTTPException

s3 = boto3.client('s3', aws_access_key_id=S3_KEY, 
                  aws_secret_access_key=S3_SECRET)

def upload_file(file, bucket, key):
    try:
        s3.upload_file(file, bucket, key)
    except (BotoCoreError, NoCredentialsError) as e:
        raise HTTPException(status_code=400, detail=str(e))

def download_file(bucket, key):
    try:
        s3.download_file(bucket, key, key)
    except (BotoCoreError, NoCredentialsError) as e:
        raise HTTPException(status_code=400, detail=str(e))

# other helpers
