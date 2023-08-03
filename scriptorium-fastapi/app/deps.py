from fastapi import Depends
from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_KEY
from fastapi.security import OAuth2PasswordBearer

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Validate JWT token with Supabase
    payload = supabase.auth.get_user(token)
    return payload.get('user')
