# Supabase Client Setup
# Simple client initialization for database and storage

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Service role key for backend

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in environment variables")

# Initialize Supabase client (singleton)
_supabase_client: Client = None

def get_supabase_client() -> Client:
    """Get or create Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("✅ Supabase client initialized (service_role)")
    return _supabase_client

