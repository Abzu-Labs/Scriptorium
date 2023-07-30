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


