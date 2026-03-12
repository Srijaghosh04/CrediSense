import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

if supabase_url and supabase_key:
    supabase: Client = create_client(supabase_url, supabase_key)
else:
    print("WARNING: SUPABASE_URL or SUPABASE_KEY is missing. Database operations will fail.")
    supabase = None


class Database:
    @property
    def client(self) -> Client:
        if not supabase:
            raise Exception("Supabase client not initialized. Please set SUPABASE_URL and SUPABASE_KEY.")
        return supabase

db = Database()

applications_db = {}    
documents_db = {}       
insights_db = {}        
research_db = {}        
cam_reports_db = {}
