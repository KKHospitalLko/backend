from decimal import Decimal
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, desc, func, select, text
from database import engine
from models.bill_model import FinalBillSummary
from schemas.bill_schema import FinalBillSummaryCreate, PatientDetailsShowSchemaForBill, BedDetailsShowSchemaForBill, AllTransactionSummaryShowSchemaForBill, FinalBillSummaryShowSchema, UpdateBillSchema
from models.bed_model import BedDetails
from models.patient_model import PatientDetails
from models.transaction_model import TransactionSummary
from models import bill_model


router= APIRouter(tags=['Bills'])

def create_db_and_tables():

    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS finalbillsummary CASCADE"))
        conn.commit()
        
    bill_model.FinalBillSummary.__table__.drop(engine, checkfirst=True)
    bill_model.FinalBillSummary.__table__.create(engine)

create_db_and_tables()


# Get a session
def get_session():
    with Session(engine) as session:
        yield session



def prepare_json_for_db(data):
    if isinstance(data, Decimal):
        return round(float(data), 2)  # Convert and round to 2 decimal places
    elif isinstance(data, float):
        return round(data, 2)  # Already float, just round
    elif isinstance(data, list):
        return [prepare_json_for_db(i) for i in data]
    elif isinstance(data, dict):
        return {k: prepare_json_for_db(v) for k, v in data.items()}
    return data


@router.post("/final-bill", response_model=FinalBillSummaryShowSchema)
def create_final_bill(req: FinalBillSummaryCreate, db: Session = Depends(get_session)):

    existing_bill = db.exec(
    select(FinalBillSummary)
    .where(FinalBillSummary.final_bill_no == req.final_bill_no)
    .order_by(
        desc(FinalBillSummary.id)
    )
    ).first()

    # print(existing_bill)

    if existing_bill and existing_bill.status=='ACTIVE':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Final bill already exists for UHID {req.patient_uhid}"
        )
    
    charges = prepare_json_for_db([item.model_dump() for item in req.charges_summary]) if req.charges_summary else None
    txns = prepare_json_for_db([item.model_dump() for item in req.transaction_breakdown]) if req.transaction_breakdown else None
    new_bill = FinalBillSummary(
        final_bill_no=req.final_bill_no,
        patient_uhid=req.patient_uhid,
        patient_regno=req.patient_regno,
        patient_name=req.patient_name,
        age=req.age,
        gender=req.gender,
        admission_date=req.admission_date,
        discharge_date=req.discharge_date,
        discharge_time=req.discharge_time,
        consultant_doctor=req.consultant_doctor,
        room_type=req.room_type,
        bed_no=req.bed_no,
        charges_summary=charges,  
        transaction_breakdown=txns,  
        medication_discount=req.medication_discount,
        room_service_discount=req.room_service_discount,
        consultancy_charges_discount=req.consultancy_charges_discount,
        total_charges=req.total_charges,
        total_discount=req.total_discount,
        net_amount=req.net_amount,
        total_paid=req.total_paid,
        balance=req.balance,
        created_by=req.created_by
    )

    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)
    return new_bill



@router.get('/final-bill/{uhid}', response_model=List[FinalBillSummaryShowSchema])
def get_final_bill_uhid(
    uhid: str,
    db: Session = Depends(get_session)
):
    bill = db.exec(
    select(FinalBillSummary)
    .where(FinalBillSummary.patient_uhid == uhid)
    .order_by(
        desc(FinalBillSummary.id)
    )
    ).all()

    if not bill:
        raise HTTPException(status_code=404, detail=f"No bill found for UHID {uhid}")

    return bill




@router.put("/final-bill/cancel/{billno}", response_model=FinalBillSummaryShowSchema)
def cancel_transaction(
    billno: str,
    req: UpdateBillSchema,
    db: Session = Depends(get_session)
    ):
    
    bill = db.exec(
    select(FinalBillSummary)
    .where(FinalBillSummary.final_bill_no == billno)
    .order_by(
        desc(FinalBillSummary.id)
    )
    ).first()

    if not bill:
        raise HTTPException(status_code=404, detail=f"Bill {billno} not found")

    if bill.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Bill is already cancelled")

    bill.status = "cancelled"
    bill.cancelled_by = req.cancelled_by

    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill





@router.get('/patient/bed/transaction/{uhid}/forbill', response_model=dict)
def get_bed_by_uhid(uhid: str, db: Session = Depends(get_session)):
    # Query PatientDetails by uhid to get the most recent regno
    patient = db.exec(
        select(PatientDetails)
        .where(PatientDetails.uhid == uhid)
        .order_by(PatientDetails.regno.desc())
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail=f"No patient found with UHID {uhid}")

    # Check if a bill already exists for this patient + latest regno
    existing_bill = db.exec(
        select(FinalBillSummary)
        .where(
            (FinalBillSummary.patient_uhid == patient.uhid) &
            (FinalBillSummary.patient_regno == patient.regno) &
            (FinalBillSummary.status == "ACTIVE")
        )
    ).first()

    if existing_bill:
        raise HTTPException(
            status_code=400,
            detail=f"An active bill already exists for UHID {uhid}, Regno {patient.regno}"
        )

    # Query BedDetails by uhid
    beds = db.exec(select(BedDetails).where(BedDetails.uhid == uhid)).first()

    # Query all ACTIVE transactions for the most recent regno
    transactions = db.exec(
        select(TransactionSummary)
        .where(
            (TransactionSummary.patient_uhid == patient.uhid) &
            (TransactionSummary.patient_regno == patient.regno) &
            (TransactionSummary.status == "ACTIVE")
        )
        .order_by(TransactionSummary.id.desc())   # latest first
    ).all()

    # Prepare response
    response = {
        "patient": PatientDetailsShowSchemaForBill.model_validate(patient),
        "beds": BedDetailsShowSchemaForBill.model_validate(beds) if beds else None,
        "transactions": [AllTransactionSummaryShowSchemaForBill.model_validate(transaction) for transaction in transactions] if transactions else []
    }

    return response