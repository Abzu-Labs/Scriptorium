# main.py

from fastapi import FastAPI
from app.routes import router
from app.config import SUPABASE_URL, SUPABASE_KEY 

app = FastAPI()

# Initialize clients
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app.include_router(router)