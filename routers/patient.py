from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, timezone
from sqlmodel import Session, func, select, text
import models.patient_model as patient_model
import schemas.patient_schemas as patient_schemas
from database import engine
import pytz
from models.bill_model import FinalBillSummary


router = APIRouter(tags=["Patient"])

def create_db_and_tables():
    
    # with engine.connect() as conn:
    #     conn.execute(text("DROP TABLE IF EXISTS patientdetails CASCADE"))
    #     conn.commit()

    patient_model.PatientDetails.__table__.drop(engine, checkfirst=True)
    patient_model.PatientDetails.__table__.create(engine)

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

    new_regno = f"{1:03d}"
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
        # bloodGroup=req.bloodGroup,
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

    new_regno_int = int(existing_patient.regno) + 1
    new_regno= f"{new_regno_int:03d}"
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
        # bloodGroup=req.bloodGroup if req.bloodGroup is not None else existing_patient.bloodGroup,
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



# @router.get('/patient/all', response_model= List[patient_schemas.PatientDetailsSearchResponseSchema])
# def get_all_patients_before_discharge(db: Session = Depends(get_session)):
#     # Step 1: Get each patient's latest regno
#     latest_regnos = db.exec(
#         select(
#             patient_model.PatientDetails.uhid,
#             func.max(patient_model.PatientDetails.regno).label("latest_regno")
#         ).group_by(patient_model.PatientDetails.uhid)
#     ).all()

#     results = []

#     # Step 2: For each latest patient regno, check if bill exists
#     for uhid, latest_regno in latest_regnos:
#         patient = db.exec(
#             select(patient_model.PatientDetails)
#             .where(
#                 (patient_model.PatientDetails.uhid == uhid) &
#                 (patient_model.PatientDetails.regno == latest_regno)
#             )
#         ).first()

#         # Skip if active bill exists
#         existing_bill = db.exec(
#             select(FinalBillSummary)
#             .where(
#                 (FinalBillSummary.patient_uhid == uhid) &
#                 (FinalBillSummary.patient_regno == latest_regno) &
#                 (FinalBillSummary.status == "ACTIVE")
#             )
#         ).first()

#         if not existing_bill and patient:
#             results.append(patient)

#     # 'results' now contains all patients of their latest regno without active bills





# # This route give you the details with the array of transactions
# @router.get('/patient/{uhid}/with-transactions', response_model=patient_schemas.PatientDetailsWithTransactionsSchema)
# def get_patient_with_transactions(uhid: str, db: Session = Depends(get_session)):
#     from models.transaction_model import TransactionSummary
    
#     # Get latest patient
#     patient = db.exec(
#         select(patient_model.PatientDetails)
#         .where(patient_model.PatientDetails.uhid == uhid)
#         .order_by(patient_model.PatientDetails.regno.desc())
#     ).first()
    
#     if not patient:
#         raise HTTPException(status_code=404, detail=f"No patient found with UHID {uhid}")
    
#     # ✅ FIX: Get transactions for LATEST REGNO ONLY
#     transactions = db.exec(
#         select(TransactionSummary)
#         .where(
#             TransactionSummary.patient_uhid == uhid,
#             TransactionSummary.patient_regno == patient.regno  # Add this filter for latest regno
#         )
#         .order_by(TransactionSummary.transaction_date.desc())
#     ).all()
    

#     # Convert transactions
#     transaction_list = [
#         patient_schemas.TransactionInPatientSchema(
#             id=t.id,
#             patient_regno=t.patient_regno,
#             transaction_purpose=t.transaction_purpose,
#             amount=t.amount,
#             payment_mode=t.payment_mode,
#             payment_details=t.payment_details,  # Add this line
#             transaction_date=t.transaction_date,
#             transaction_time=t.transaction_time,
#             transaction_no=t.transaction_no,
#             created_by=t.created_by
#         ) for t in transactions
#     ]

#     return patient_schemas.PatientDetailsWithTransactionsSchema(
#         uhid=patient.uhid,
#         title=patient.title,
#         fullname=patient.fullname,
#         sex=patient.sex,
#         mobile=patient.mobile,
#         dateofreg=patient.dateofreg,
#         regno=patient.regno,
#         time=patient.time,
#         age=patient.age,
#         empanelment=patient.empanelment,
#         religion=patient.religion,
#         maritalStatus=patient.maritalStatus,
#         fatherHusband=patient.fatherHusband,
#         doctorIncharge=patient.doctorIncharge,
#         regAmount=patient.regAmount,
#         localAddress=patient.localAddress,
#         permanentAddress=patient.permanentAddress,
#         registered_by=patient.registered_by,
#         transactions=transaction_list
#     )


