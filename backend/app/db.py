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
