# main.py

from fastapi import FastAPI
from app.routes import router as api_router

app = FastAPI()

# Initialize clients
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app.include_router(router)