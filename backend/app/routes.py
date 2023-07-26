from fastapi import APIRouter, Depends, UploadFile
from typing import List
from app.models import Project, ProjectCreate, File, FileOrder  
from app.db import supabase

router = APIRouter()

@router.post("/projects", response_model=Project)
def create_project(project: ProjectCreate, user: dict = Depends(get_user)):
  new_project = supabase.table('projects').insert(project).execute()

  return new_project

@router.get("/projects", response_model=List[Project]) 
def get_projects(user: dict = Depends(get_user)):
  user_projects = supabase.table('projects') \
                     .select() \
                     .match({owner_id: user['id']}) \
                     .execute()
  
  return user_projects 

@router.post("/files")
def upload_file(file: UploadFile, project_id: int):

  filename = file.filename
  s3_path = upload_to_s3(file, project_id) 

  new_file = File(name=filename, project_id=project_id)
  supabase.table('files').insert(new_file).execute()

  return {
    "id": new_file.id,
    "path": s3_path
  }

@router.get("/files") 
def get_files(project_id: int):
  files = supabase.table('files') \
                .select() \
                .match({project_id: project_id})
  
  return files

# Voice samples endpoints 

@router.post("/voice-samples")
def upload_voice_sample(file: UploadFile, user: dict = Depends(get_user)):

  s3_path = upload_to_s3(file, user['id'])

  record = {user_id: user['id'], file_path: s3_path}

  supabase.table('voice_samples').insert(record).execute()

  return {
    "path": s3_path 
  }

@router.get("/voice-samples")
def get_voice_samples(user: dict = Depends(get_user)):

  samples = supabase.table('voice_samples') \
                 .select() \
                 .match({user_id: user['id']})
  
  return samples