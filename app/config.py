import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SUPABASE_URL = os.environ.get('https://xibexzbpueobbznwotlv.supabase.co')
    SUPABASE_KEY = os.environ.get('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhpYmV4emJwdWVvYmJ6bndvdGx2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjI1OTY1ODAsImV4cCI6MjAzODE3MjU4MH0.wzM6gsucXBpfRBQWRhJw5y5n1ReKeejyTLnC-2ahadM')
    # Add other configuration variables as needed