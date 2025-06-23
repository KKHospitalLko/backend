from fastapi import Depends, FastAPI
from typing import Optional
import models
import schemas
from database import engine
from sqlmodel import Session

app= FastAPI()

# Create tables
def create_db_and_tables():
    models.SQLModel.metadata.create_all(engine)

# Call this function when FastAPI starts
create_db_and_tables()


# Get a session
def get_session():
    with Session(engine) as session:
        yield session

@app.post('/patient')
def admitPatient(req: schemas.PatientDetailsSchema, db: Session= Depends(get_session)):
    new_patient= models.PatientDetails(
        fullname= req.fullname,
        department= req.department
    )
    
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient