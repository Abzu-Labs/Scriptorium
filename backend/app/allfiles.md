I am of rewriting, the backend of a Supabase application made with fast API I've that my attempts to create a user system were flawed in the sense that they generated a user ID as an INT eight value, which did not reference your authorization UID created by the super base library, which was I use the platform in the first place, and all subsequent data models relied on that faulty user construction so now I have the best of my abilities on my own Ed data model, but want to check through the assumptions as were through the ramifications which these changes to my models.py well necessitate on the rest of my backend

the directory structure is at present:

/Users/jake/dev/scriptorium/backend
├── app
│   ├── allfiles.txt
│   ├── config.py
│   ├── db.py
│   ├── deps.py
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   ├── s3.py
│   └── utils.py
├── dockerfile
└── tests
    └── test_main.py

Where the /Scriptorium directory will contain both the front and backend modules but at the moment the fastapi system is entirely located in /Scriptorium/backend and relies on only the requirements.txt and .env files within the application root directory

# config.py

from dotenv import load_dotenv
import os

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

# models.py
from pydantic import BaseModel

class User(BaseModel):
    id: str
    aud: str
    role: str
    email: str
    app_metadata: dict
    user_metadata: dict

class Project(BaseModel):
    id: int
    name: str
    owner_id: str

class ProjectCreate(Project):
    pass

class File(BaseModel):
    id: int
    name: str
    text_content: Optional[str] = None


class ProjectSequence(BaseModel):
    project_id: int
    files: List[int]

class TTSRequest(BaseModel):
    source_file_id: Optional[int] = None
    text: str
    voice_id: str  # The user will select one of the available voice IDs
    file_id: int

class UserVoice(BaseModel):
    user_id: str
    voice_id: str
    date_created: datetime


class SampleFile(File):


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

 # utils.py

from docx import Document
import PyPDF2

def extract_text(file):
    if file.content_type == "application/pdf":
        pdf_reader = PyPDF2.PdfFileReader(file.file)
        text = " ".join(page.extractText() for page in pdf_reader.pages)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file.file)
        text = " ".join(paragraph.text for paragraph in doc.paragraphs)
    else:
        raise ValueError(f"Unsupported file type: {file.content_type}")
    return text
# db.py

from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY
from fastapi import HTTPException

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def get_users():
    try:
        res = await supabase.table('users').select('*').execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def create_user(user):
    try:
        res = await supabase.table('users').insert(user).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# and other db helper functions
from supabase_py import create_client, session

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def get_current_user(token: str = Depends(session)):
    # Validate JWT token with Supabase
    payload = supabase.auth.get_user(token)
    return payload.get('user')

    # main.py

from fastapi import FastAPI
from app.routes import router as api_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(api_router, prefix="/api")

# routes.py
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from app.models import Project, ProjectCreate, File as FileModel, FileOrder
from app.db import supabase
from .auth import get_current_user
from elevenlabs.base import API
from .utils import extract_text

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
    supabase.table('user_voices').insert({'voice_id': voice.voice_id, 'user_id': user['id']}).execute()
    return {"voice_id": voice.voice_id}
  except UnauthorizedVoiceCloningError:
    raise HTTPException(status_code=403, detail="Unauthorized voice cloning")
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))


@router.get("/voices")
def get_voices(user: dict = Depends(get_current_user)):
  try:
    # Query the user_voices table for all voices of the current user
    user_voices = supabase.table('user_voices').select().match({'user_id': user['id']}).execute()

    # Format the response data to only return the voice IDs
    voice_ids = [voice['voice_id'] for voice in user_voices['data']]

    return voice_ids
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
