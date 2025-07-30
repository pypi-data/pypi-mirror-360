# openmailer/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load .env from project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(dotenv_path=os.path.join(project_root, '.env'))

# Check for direct DATABASE_URL (preferred in cloud environments)
DATABASE_URL = os.getenv("OM_DATABASE_URL")

if not DATABASE_URL:
    # Fallback to manual config (hosted/local dev)
    DB_HOST = os.getenv("OM_DB_HOST", "localhost")
    DB_PORT = os.getenv("OM_DB_PORT", "5432")
    DB_NAME = os.getenv("OM_DB_NAME", "openmailer")
    DB_USER = os.getenv("OM_DB_USER", "openmaileruser")
    DB_PASS = os.getenv("OM_DB_PASS")

    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Initialize engine + session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

