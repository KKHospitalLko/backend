from sqlmodel import create_engine
from dotenv import load_dotenv
import os

DATABASE_URL = "sqlite:///./kkHospital.db"

# Load environment variables from .env file
load_dotenv()

Prod_DB_URL = os.getenv("Prod_DB_URL")


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# engine = create_engine(Prod_DB_URL)