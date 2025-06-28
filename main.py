from fastapi import Depends, FastAPI, HTTPException
from typing import Optional
import models
import schemas
from database import engine
from sqlmodel import Session, select
from datetime import datetime

app = FastAPI()

# Create tables
def create_db_and_tables():
    models.SQLModel.metadata.drop_all(engine)  # Drop existing tables
    models.SQLModel.metadata.create_all(engine)  # Recreate tables

create_db_and_tables()

# Get a session
def get_session():
    with Session(engine) as session:
        yield session

# Helper function to generate UHID and registration number
def generate_ids(db: Session, existing_uhid: Optional[str] = None) -> tuple:
    # Generate UHID: YYMM + 4-digit serial number
    current_time = datetime.now()
    time_str = current_time.strftime("%y%m")  # Format: YYMM (e.g., 2506 for June 2025)

    if existing_uhid:
        # Reuse existing UHID for returning patient
        new_uhid = existing_uhid
    else:
        # Get the latest UHID to determine the serial number for the current YYMM
        result = db.exec(select(models.PatientDetails.uhid).order_by(models.PatientDetails.uhid.desc()))
        last_uhid = result.first()

        # Extract serial number from the last UHID or reset to 1 if month changes
        if last_uhid and last_uhid.startswith(time_str):
            serial_no = int(last_uhid[-4:]) + 1  # Increment the last 4 digits
        else:
            serial_no = 1  # Reset to 0001 for new YYMM (month change)

        # Ensure serial_no is 4 digits
        new_uhid = f"{time_str}{serial_no:04d}"

    # Generate registration number (always 1 for new patients)
    new_regno = 1

    return new_uhid, new_regno

@app.post('/patient', response_model=schemas.PatientDetailsResponseSchema)
def create_patient(req: schemas.PatientDetailsCreateSchema, db: Session = Depends(get_session)):
    uhid, regno = generate_ids(db)
    new_patient = models.PatientDetails(
        uhid=uhid,
        title=req.title,
        fullname=req.fullname,
        department=req.department,
        sex=req.sex,
        mobile=req.mobile,
        dateofreg=req.dateofreg,
        regno=regno,
        time=req.time,
        age=req.age,
        occupation=req.occupation,
        empanelment=req.empanelment,
        bloodGroup=req.bloodGroup,
        religion=req.religion,
        intimationOrExtension=req.intimationOrExtension,
        maritalStatus=req.maritalStatus,
        fatherHusband=req.fatherHusband,
        refDocName=req.refDocName,
        refDocTel=req.refDocTel,
        purposeForVisit=req.purposeForVisit,
        doctorIncharge=req.doctorIncharge,
        regAmount=req.regAmount,
        notes=req.notes,
        localAddress=req.localAddress.model_dump() if req.localAddress else None,
        permanentAddress=req.permanentAddress.model_dump() if req.permanentAddress else None
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@app.get('/patient/{search_value}', response_model=list[schemas.PatientDetailsResponseSchema])
def get_patient_by_uhid_or_mobile(search_value: str, db: Session = Depends(get_session)):
    # Try converting search_value to int to check if it could be a mobile number
    try:
        mobile_value = int(search_value)
    except ValueError:
        mobile_value = None

    # Build query to search by uhid or mobile
    query = select(models.PatientDetails)
    if mobile_value is not None:
        query = query.where(
            (models.PatientDetails.uhid == search_value) |
            (models.PatientDetails.mobile == mobile_value)
        )
    else:
        query = query.where(models.PatientDetails.uhid == search_value)

    result = db.exec(query.order_by(models.PatientDetails.regno.desc()))
    patients = result.all()
    if not patients:
        raise HTTPException(status_code=404, detail=f"No patients found with UHID or mobile {search_value}")
    return patients

@app.put('/patient/{uhid}', response_model=schemas.PatientDetailsResponseSchema)
def update_patient_by_uhid(uhid: str, req: schemas.PatientDetailsUpdateSchema, db: Session = Depends(get_session)):
    # Find the latest patient record by UHID
    result = db.exec(select(models.PatientDetails).where(models.PatientDetails.uhid == uhid).order_by(models.PatientDetails.regno.desc()))
    existing_patient = result.first()
    if not existing_patient:
        raise HTTPException(status_code=404, detail=f"Patient with UHID {uhid} not found")

    # Get current regno and increment it
    new_regno = existing_patient.regno + 1

    # Reuse the same UHID
    new_uhid, _ = generate_ids(db, existing_uhid=uhid)

    # Create a new patient record
    new_patient = models.PatientDetails(
        uhid=new_uhid,
        title=req.title,
        fullname=req.fullname,
        department=req.department,
        sex=req.sex,
        mobile=req.mobile,
        dateofreg=req.dateofreg,
        regno=new_regno,
        time=req.time,
        age=req.age,
        occupation=req.occupation,
        empanelment=req.empanelment,
        bloodGroup=req.bloodGroup,
        religion=req.religion,
        intimationOrExtension=req.intimationOrExtension,
        maritalStatus=req.maritalStatus,
        fatherHusband=req.fatherHusband,
        refDocName=req.refDocName,
        refDocTel=req.refDocTel,
        purposeForVisit=req.purposeForVisit,
        doctorIncharge=req.doctorIncharge,
        regAmount=req.regAmount,
        notes=req.notes,
        localAddress=req.localAddress.model_dump() if req.localAddress else None,
        permanentAddress=req.permanentAddress.model_dump() if req.permanentAddress else None
    )
    
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@app.get('/patient', response_model=list[schemas.PatientDetailsResponseSchema])
def get_all_patients(db: Session = Depends(get_session)):
    result = db.exec(select(models.PatientDetails))
    return result.all()