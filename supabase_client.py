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
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")  # Anon key for user operations

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in environment variables")

# Initialize Supabase clients (singleton)
_supabase_service_client: Client = None
_supabase_anon_client: Client = None

def get_supabase_client() -> Client:
    """Get or create Supabase service client instance (bypasses RLS)."""
    global _supabase_service_client
    if _supabase_service_client is None:
        _supabase_service_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("✅ Supabase service client initialized (service_role)")
    return _supabase_service_client

def get_supabase_anon_client() -> Client:
    """Get or create Supabase anon client instance (respects RLS)."""
    global _supabase_anon_client
    if _supabase_anon_client is None:
        if not SUPABASE_ANON_KEY:
            raise ValueError("Missing SUPABASE_ANON_KEY in environment variables")
        _supabase_anon_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        print("✅ Supabase anon client initialized (anon_key)")
    return _supabase_anon_client

