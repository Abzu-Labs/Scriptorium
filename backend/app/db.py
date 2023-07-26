from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def get_users():
    res = await supabase.table('users').select('*').execute()
    return res.data

async def create_user(user):
    res = await supabase.table('users').insert(user).execute()
    return res.data

# and other db helper functions