# s3.py

import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError
from app.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from fastapi import HTTPException

s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

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
    