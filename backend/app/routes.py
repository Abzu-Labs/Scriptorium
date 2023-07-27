from fastapi import APIRouter, Depends, HTTPException, UploadFile
from typing import List
from app.models import Project, ProjectCreate, File, FileOrder  
from app.db import supabase
from fastapi.security import OAuth2PasswordBearer
from .auth import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

@router.post("/projects", response_model=Project)
def create_project(project: ProjectCreate, user: dict = Depends(get_user)):
    try:
        new_project = supabase.table('projects').insert(project).execute()
        return new_project
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/projects", response_model=List[Project]) 
def get_projects(user: dict = Depends(get_user)):
    try:
        user_projects = supabase.table('projects') \
                            .select() \
                            .match({owner_id: user['id']}) \
                            .execute()
        return user_projects
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# routes.py continued...

@router.post("/files")
def upload_file(file: UploadFile, project_id: int, user: dict = Depends(get_current_user)):
  try:
    filename = file.filename
    s3_path = upload_to_s3(file, project_id)

    new_file = File(name=filename, project_id=project_id)
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
def upload_voice_sample(file: UploadFile, user: dict = Depends(get_current_user)):
  try:
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
async def generate_tts(request: TTSRequest, user: dict = Depends(get_current_user)):
  try:
    response = call_elevenlabs_api(request.text, request.voice_id)

    # Process response and upload to S3
    audio_file = process_audio(response)
    s3_path = upload_to_s3(audio_file, "tts-output/")

    return {"audio_path": s3_path}
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
