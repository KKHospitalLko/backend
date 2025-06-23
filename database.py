from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./kkHospital.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})