from supabase_py import create_client, session

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) 

async def get_current_user(token: str = Depends(session)):
    # Validate JWT token with Supabase
    payload = supabase.auth.get_user(token) 
    return payload.get('user')