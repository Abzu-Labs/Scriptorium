# routes.py
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from app.models import Project, ProjectCreate, File as FileModel, FileOrder
from app.db import supabase
from .auth import get_current_user
from elevenlabs.base import API

API.api_key = os.getenv("ELEVEN_API_KEY")

from elevenlabs import Voice, VoiceDesign, VoiceClone, Gender, Age, Accent



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
                            .match({'owner_id': user['id']}) \
                            .execute()
        return user_projects
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/files")
def upload_file(file: UploadFile = File(...), project_id: int, user: dict = Depends(get_current_user)):
    try:
        # Check file size
        if len(file.file.read()) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File size exceeds limit")

        # Check file type
        if file.content_type not in ["application/pdf", "image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="File type not supported")

        # Reset file to start
        file.file.seek(0)

        filename = file.filename
        s3_path = upload_to_s3(file, project_id)

        new_file = FileModel(name=filename, project_id=project_id)
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
                    .match({'project_id': project_id, 'owner_id': user['id']}) \
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

@router.post("/tts")
async def generate_tts(text: str, voice_id: str, user: dict = Depends(get_current_user)):
  try:
    # Create a voice design
    voice_design = VoiceDesign(
      name="User Voice",
      text=text,
      gender=Gender.female,  # replace with actual gender
      age=Age.middle_aged,  # replace with actual age
      accent=Accent.american,  # replace with actual accent
      accent_strength=1.0,  # replace with actual accent strength
    )
    # Generate the voice
    audio = voice_design.generate()
    # Upload the audio to S3
    s3_path = upload_to_s3(audio, "tts-output/")
    return {"audio_path": s3_path}
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

@router.post("/voice-clone")
def create_voice_clone(voice_clone: VoiceClone, user: dict = Depends(get_current_user)):
  try:
    # Create a voice from the voice clone
    voice = Voice.from_clone(voice_clone)
    # Add the new voice ID to the voices table in Supabase
    supabase.table('voices').insert({'voice_id': voice.voice_id, 'user_id': user['id']}).execute()
    return {"voice_id": voice.voice_id}
  except UnauthorizedVoiceCloningError:
    raise HTTPException(status_code=403, detail="Unauthorized voice cloning")
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
  

@router.get("/voices")
def get_voices(user: dict = Depends(get_current_user)):
  try:
    # Query the voices table for all voices of the current user
    user_voices = supabase.table('voices').select().match({'user_id': user['id']}).execute()
    return user_voices
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
