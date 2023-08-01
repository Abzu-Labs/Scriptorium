from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class File(BaseModel):
    id: int
    name: Optional[str] = None
    type: Optional[str] = None
    size: Optional[int] = None
    created_at: Optional[datetime] = None
    user_id: Optional[UUID] = None
    speech_sample: Optional[bool] = None


class Project(BaseModel):
    id: int
    user_id: Optional[UUID] = None
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    cover_image: Optional[int] = None


class User(BaseModel):
    user_id: UUID
    email: Optional[str] = None


class Voice(BaseModel):
    id: str
    name: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    accent: Optional[str] = None
    icon: Optional[str] = None


class ProjectFile(BaseModel):
    file_id: int
    project_id: int
    sequencing: Optional[int] = None
    modified_at: Optional[datetime] = None
    num_characters: Optional[int] = None


class SynthesizedAudio(BaseModel):
    id: int
    initiated_at: Optional[datetime] = None
    successful: Optional[bool] = None
    source_file: Optional[int] = None
    synthesized_audio: Optional[int] = None
    voice_used: Optional[str] = None
    audio_length: Optional[int] = None


class CustomVoice(BaseModel):
    voice_id: str
    created_at: Optional[datetime] = None
    user_id: Optional[UUID] = None


class Export(BaseModel):
    id: int
    created_at: Optional[datetime] = None
    project_id: Optional[int] = None
    audio_length: Optional[int] = None
