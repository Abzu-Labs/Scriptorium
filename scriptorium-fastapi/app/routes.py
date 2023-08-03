import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from app.models import Project, ProjectCreate, File as FileModel, FileOrder
from app.db import supabase
from supabase import get_current_user
from .utils import extract_text
import requests
import boto3
from datetime import datetime
from requests_toolbelt.multipart import encoder
from s3 import upload_file as upload_to_s3
from config import ELEVEN_API_KEY

s3 = boto3.client('s3', region_name='us-east-1')


router = APIRouter()

@router.post("/projects", response_model=Project)
def create_project(project: ProjectCreate, user: dict = Depends(get_current_user)):
    try:
        new_project = supabase.table('projects').insert(project.dict()).execute()
        return new_project
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/projects", response_model=List[Project])
def get_projects(user: dict = Depends(get_current_user)):
    try:
        user_projects = supabase.table('projects') \
                            .select() \
                            .match({'user_id': user['id']}) \
                            .execute()
        return user_projects
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/files")
def upload_file(project_id: int, file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    try:
        # Check file size
        if len(file.file.read()) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File size exceeds limit")

        # Check file type
        if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="File type not supported")

        # Reset file to start
        file.file.seek(0)

        filename = file.filename
        s3_path = upload_to_s3(file, project_id)

        # Extract text if it's a PDF or DOCX file
        if file.content_type in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            text_content = extract_text(file)
        else:
            text_content = None

        new_file = FileModel(name=filename, project_id=project_id, text_content=text_content)
        file_response = supabase.table('files').insert(new_file.dict()).execute()

        if not file_response:
            raise HTTPException(status_code=400, detail="Failed to insert file.")

        return {
            "id": new_file.id,
            "path": s3_path
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/files")
def get_files(project_id: int, user: dict = Depends(get_current_user)):
    try:
        files = supabase.table('files') \
                    .select() \
                    .match({'project_id': project_id, 'user_id': user['id']}) \
                    .execute()

        if not files:
            raise HTTPException(status_code=400, detail="Failed to retrieve files.")

        return files
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Voice samples endpoints

@router.post("/voice-samples")
def upload_voice_sample(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    try:
        # Check file size
        if len(file.file.read()) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File size exceeds limit")

        # Check file type
        if file.content_type not in ["audio/mpeg", "audio/wav"]:
            raise HTTPException(status_code=400, detail="File type not supported")

        # Reset file to start
        file.file.seek(0)

        s3_path = upload_to_s3(file, user['id'])

        record = {'user_id': user['id'], 'file_path': s3_path}

        sample_response = supabase.table('voice_samples').insert(record).execute()

        if not sample_response:
            raise HTTPException(status_code=400, detail="Failed to insert voice sample.")

        return {
            "path": s3_path
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/voice-samples")
def get_voice_samples(user: dict = Depends(get_current_user)):
    try:
        samples = supabase.table('voice_samples') \
                    .select() \
                    .match({'user_id': user['id']}) \
                    .execute()

        if not samples:
            raise HTTPException(status_code=400, detail="Failed to retrieve voice samples.")

        return samples
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/voice-clone")
async def create_voice_clone(voice_name: str, user: dict = Depends(get_current_user)):
    try:
        # Fetch all the files associated with the user and marked as speech_sample=true
        files_response = supabase.table('file') \
                            .select('*') \
                            .match({'user_id': user['user_id'], 'speech_sample': True}) \
                            .execute()

        if not files_response or 'data' not in files_response:
            raise HTTPException(status_code=400, detail="Failed to retrieve voice samples.")

        files = []
        # For each file, download it from S3 and add it to the files list
        for file in files_response['data']:
            file_path = file['name']  # Replace 'name' with the actual column name for the file path in S3
            s3_file = s3.download_file('scriptorium-app', file_path)
            files.append(('file', (file_path, open(s3_file, 'rb'), 'audio/mpeg')))

        # Set the URL for the API endpoint
        url = "https://api.elevenlabs.io/v1/voices/add"

        # Set the headers for the request
        headers = {
            "accept": "application/json",
            "xi-api-key": os.getenv("ELEVEN_API_KEY"),
        }

        # Prepare the data for the request
        data = {"name": voice_name}

        # Create a multipart encoded form with the files
        multipart_data = encoder.MultipartEncoder(
            fields={**data, **{f"file_{i}": (file.filename, file.file, file.content_type) for i, file in enumerate(files)}}
        )

        # Update headers with the correct content type
        headers["Content-Type"] = multipart_data.content_type

        # Send the request to the API
        response = requests.post(url, headers=headers, data=multipart_data)

        # Check if the request was successful
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to clone voice.")
        voice_id = response.json().get("voice_id")

        if not voice_id:
            raise HTTPException(status_code=400, detail="Failed to get voice_id.")

        # Add the new voice ID to the custom_voice table in Supabase
        new_voice = {
            "voice_id": voice_id,
            "created_at": datetime.now(),
            "user_id": user['user_id'],
        }
        voice_response = supabase.table('custom_voice').insert(new_voice).execute()
        if not voice_response:
            raise HTTPException(status_code=400, detail="Failed to insert voice.")

        return {"voice_id": voice_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/voices")
def get_voices(user: dict = Depends(get_current_user)):
    try:
        # Query the user_voices table for all voices of the current user
        user_voices = supabase.table('custom_voice') \
                    .select() \
                    .match({'user_id': user['user_id']}) \
                    .execute()

        # Format the response data to only return the voice IDs
        voice_ids = [voice['voice_id'] for voice in user_voices['data']]

        return voice_ids
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
