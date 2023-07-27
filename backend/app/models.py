# models.py
from pydantic import BaseModel

class User(BaseModel):
    id: str
    aud: str
    role: str
    email: str
    confirmation_sent_at: str
    confirmed_at: str
    last_sign_in_at: str
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
    project_id: int
    text_content: Optional[str] = None


class FileOrder(BaseModel):
    files: List[int]

class TTSRequest(BaseModel):
    text: str
    voice_id: str  # The user will select one of the available voice IDs
    file_id: int

class UserVoice(BaseModel):
    user_id: str
    voice_id: str
