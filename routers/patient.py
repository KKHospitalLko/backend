from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Session, select
import models.patient_model as patient_model
import schemas.patient_schemas as patient_schemas
from database import engine
import pytz

router = APIRouter(tags=["Patient"])

def create_db_and_tables():
    # patient_model.SQLModel.metadata.drop_all(engine)
    patient_model.SQLModel.metadata.create_all(engine)

create_db_and_tables()

def get_session():
    with Session(engine) as session:
        yield session

def get_current_ist_time():
    """Get current IST time reliably regardless of system timezone"""
    utc_now = datetime.now(timezone.utc)
    ist_tz = pytz.timezone('Asia/Kolkata')
    ist_time = utc_now.astimezone(ist_tz)
    return ist_time

def generate_ids(db: Session, existing_uhid: Optional[str] = None) -> tuple:
    current_time_ist = get_current_ist_time()
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
    current_ist_datetime = get_current_ist_time()
    date_of_registration = current_ist_datetime.strftime("%Y-%m-%d")
    time_of_registration = current_ist_datetime.strftime("%I:%M:%S %p")

    new_patient = patient_model.PatientDetails(
        uhid=uhid,
        title=req.title,
        fullname=req.fullname,
        sex=req.sex,
        mobile=req.mobile,
        dateofreg=req.dateofreg or date_of_registration,
        regno=regno,
        time=req.time or time_of_registration,
        age=req.age,
        empanelment=req.empanelment,
        bloodGroup=req.bloodGroup,
        religion=req.religion,
        maritalStatus=req.maritalStatus,
        fatherHusband=req.fatherHusband,
        doctorIncharge=req.doctorIncharge,
        regAmount=req.regAmount,
        localAddress=req.localAddress.model_dump() if req.localAddress else None,
        permanentAddress=req.permanentAddress.model_dump() if req.permanentAddress else None,
        registered_by=req.registered_by
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@router.get('/debug-time')
def debug_time():
    import os
    current_ist = get_current_ist_time()
    utc_now = datetime.now(timezone.utc)
    return {
        "utc_time": utc_now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "ist_time": current_ist.strftime("%Y-%m-%d %H:%M:%S IST"),
        "formatted_time": current_ist.strftime("%I:%M:%S %p"),
        "TZ_env": os.environ.get('TZ', 'Not Set'),
        "system_timezone": str(datetime.now().astimezone().tzinfo)
    }

@router.get('/patient/{search_value}', response_model=list[patient_schemas.PatientDetailsSearchResponseSchema])
def get_patient_by_uhid_or_mobile(search_value: str, db: Session = Depends(get_session)):
    # Build query to search by uhid or mobile
    query = select(patient_model.PatientDetails).where(
        (patient_model.PatientDetails.uhid == search_value) |
        (patient_model.PatientDetails.mobile == search_value)
    )
    result = db.exec(query.order_by(patient_model.PatientDetails.regno.desc()))
    patients = result.all()
    if not patients:
        raise HTTPException(status_code=404, detail=f"No patients found with UHID or mobile {search_value}")
    return patients

@router.put('/patient/{uhid}', response_model=patient_schemas.PatientDetailsResponseSchema)
def update_patient_by_uhid(uhid: str, req: patient_schemas.PatientDetailsUpdateSchema, db: Session = Depends(get_session)):
    result = db.exec(select(patient_model.PatientDetails).where(patient_model.PatientDetails.uhid == uhid).order_by(patient_model.PatientDetails.regno.desc()))
    existing_patient = result.first()
    if not existing_patient:
        raise HTTPException(status_code=404, detail=f"Patient with UHID {uhid} not found")

    new_regno = existing_patient.regno + 1
    new_uhid, _ = generate_ids(db, existing_uhid=uhid)

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