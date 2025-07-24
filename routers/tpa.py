from fastapi import APIRouter
from sqlmodel import Session, select, SQLModel
from fastapi import APIRouter, Depends, HTTPException
from database import engine
from models.bed_model import BedDetails
from models.patient_model import PatientDetails
from schemas.bed_schemas import BedDetailsResponseSchema
from schemas.patient_schemas import PatientDetailsSearchResponseSchema

router = APIRouter(tags=['TPA'])

# Get a session
def get_session():
    with Session(engine) as session:
        yield session

@router.get('/bed/uhid/{uhid}', response_model=dict)
def get_bed_by_uhid(uhid: str, db: Session = Depends(get_session)):
    # Query BedDetails by uhid
    beds = db.exec(select(BedDetails).where(BedDetails.uhid == uhid)).first()
    # Query PatientDetails by uhid
    patient = db.exec(select(PatientDetails).where(PatientDetails.uhid == uhid)).first()
    # Prepare response
    response = {
        "beds": BedDetailsResponseSchema.model_validate(beds),
        "patient": PatientDetailsSearchResponseSchema.model_validate(patient) if patient else None
    }
    if not beds:
        raise HTTPException(status_code=404, detail=f"No beds found with UHID {uhid}")
    return response

