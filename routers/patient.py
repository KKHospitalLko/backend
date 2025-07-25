from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime
from sqlmodel import Session, select, text
import models.patient_model as patient_model
import schemas.patient_schemas as patient_schemas
from database import engine
import pytz


router = APIRouter(tags=["Patient"])


# Create tables
def create_db_and_tables():
    patient_model.SQLModel.metadata.drop_all(engine)  # Drop existing tables
    patient_model.SQLModel.metadata.create_all(engine)  # Recreate tables


create_db_and_tables()


# Get a session
def get_session():
    with Session(engine) as session:
        session.connection().execute(text("SET TIME ZONE 'Asia/Kolkata';"))
        yield session


# Helper function to generate UHID and registration number
def generate_ids(db: Session, existing_uhid: Optional[str] = None) -> tuple:
    ist_timezone = pytz.timezone('Asia/Kolkata')
    current_time_ist = datetime.now(ist_timezone) # Use a different variable name for clarity


    time_str = current_time_ist.strftime("%y%m")


    if existing_uhid:
        new_uhid = existing_uhid
    else:
        result = db.exec(select(patient_model.PatientDetails.uhid).order_by(patient_model.PatientDetails.uhid.desc()))
        last_uhid = result.first()


        if last_uhid and last_uhid.startswith(time_str):
            serial_no = int(last_uhid[-4:]) + 1
        else:
            serial_no = 1
        new_uhid = f"{time_str}{serial_no:04d}"


    new_regno = 1
    return new_uhid, new_regno


@router.post('/patient', response_model=patient_schemas.PatientDetailsResponseSchema)
def create_patient(req: patient_schemas.PatientDetailsCreateSchema, db: Session = Depends(get_session)):


    uhid, regno = generate_ids(db)


    # Get current IST date and time for dateofreg and time
    ist_timezone = pytz.timezone('Asia/Kolkata')
    current_ist_datetime = datetime.now(ist_timezone)


    # Convert to string format as your model expects strings
    date_of_registration = current_ist_datetime.strftime("%Y-%m-%d")  # String format
    time_of_registration = current_ist_datetime.strftime("%I:%M:%S %p")  # String format


    new_patient = patient_model.PatientDetails(
        uhid=uhid,
        title=req.title,
        fullname=req.fullname,
        sex=req.sex,
        mobile=req.mobile,
        dateofreg=req.dateofreg or date_of_registration,  # Use provided or current
        regno=regno,
        time=req.time or time_of_registration,  # Use provided or current
        age=req.age,
        empanelment=req.empanelment,
        bloodGroup=req.bloodGroup,
        religion=req.religion,
        maritalStatus=req.maritalStatus,
        fatherHusband=req.fatherHusband,
        doctorIncharge=req.doctorIncharge,  # Already a list, no need for model_dump
        regAmount=req.regAmount,
        localAddress=req.localAddress.model_dump() if req.localAddress else None,
        permanentAddress=req.permanentAddress.model_dump() if req.permanentAddress else None,
        registered_by=req.registered_by
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient


@router.get('/patient/{search_value}', response_model=list[patient_schemas.PatientDetailsSearchResponseSchema])
def get_patient_by_uhid_or_mobile(search_value: str, db: Session = Depends(get_session)):
    # Try converting search_value to int to check if it could be a mobile number
    try:
        mobile_value = int(search_value)
    except ValueError:
        mobile_value = None


    # Build query to search by uhid or mobile
    query = select(patient_model.PatientDetails)
    if mobile_value is not None:
        query = query.where(
            (patient_model.PatientDetails.uhid == search_value) |
            (patient_model.PatientDetails.mobile == mobile_value)
        )
    else:
        query = query.where(patient_model.PatientDetails.uhid == search_value)


    result = db.exec(query.order_by(patient_model.PatientDetails.regno.desc()))
    patients = result.all()
    if not patients:
        raise HTTPException(status_code=404, detail=f"No patients found with UHID or mobile {search_value}")
    return patients


@router.put('/patient/{uhid}', response_model=patient_schemas.PatientDetailsResponseSchema)
def update_patient_by_uhid(uhid: str, req: patient_schemas.PatientDetailsUpdateSchema, db: Session = Depends(get_session)):
    # Find the latest patient record by UHID
    result = db.exec(select(patient_model.PatientDetails).where(patient_model.PatientDetails.uhid == uhid).order_by(patient_model.PatientDetails.regno.desc()))
    existing_patient = result.first()
    if not existing_patient:
        raise HTTPException(status_code=404, detail=f"Patient with UHID {uhid} not found")


    # Get current regno and increment it
    new_regno = existing_patient.regno + 1


    # Reuse the same UHID
    new_uhid, _ = generate_ids(db, existing_uhid=uhid)


    # Create a new patient record
    new_patient = patient_model.PatientDetails(
        uhid=new_uhid,
        title=req.title if req.title is not None else existing_patient.title,
        fullname=req.fullname if req.fullname is not None else existing_patient.fullname,
        sex=req.sex if req.sex is not None else existing_patient.sex,
        mobile=req.mobile if req.mobile is not None else existing_patient.mobile,
        dateofreg=req.dateofreg if req.dateofreg is not None else existing_patient.dateofreg,
        regno=new_regno,
        time=req.time if req.time is not None else existing_patient.time,
        age=req.age if req.age is not None else existing_patient.age,
        empanelment=req.empanelment if req.empanelment is not None else existing_patient.empanelment,
        bloodGroup=req.bloodGroup if req.bloodGroup is not None else existing_patient.bloodGroup,
        religion=req.religion if req.religion is not None else existing_patient.religion,
        maritalStatus=req.maritalStatus if req.maritalStatus is not None else existing_patient.maritalStatus,
        fatherHusband=req.fatherHusband if req.fatherHusband is not None else existing_patient.fatherHusband,
        doctorIncharge=req.doctorIncharge if req.doctorIncharge is not None else existing_patient.doctorIncharge,
        regAmount=req.regAmount if req.regAmount is not None else existing_patient.regAmount,
        localAddress=req.localAddress.model_dump() if req.localAddress else existing_patient.localAddress,
        permanentAddress=req.permanentAddress.model_dump() if req.permanentAddress else existing_patient.permanentAddress,
        registered_by=req.registered_by if req.registered_by is not None else existing_patient.registered_by
    )
    
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient


@router.get('/patient', response_model=list[patient_schemas.PatientDetailsSearchResponseSchema])
def get_all_patients(db: Session = Depends(get_session)):
    result = db.exec(select(patient_model.PatientDetails))
    return result.all()
