from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, text
from models.patient_model import PatientDetails
from models.transaction_model import TransactionSummary
from schemas.transaction_schemas import TransactionSummaryCreate, PatientDetailsSearchSchemaForTransaction, TransactionSummaryShowSchema, AllTransactionSummaryShowSchema, UpdateTransactionSchema
from typing import List
from database import engine
import models.transaction_model as transactionModel
import models.patient_model as patient_model

def create_db_and_tables():

    # with engine.connect() as conn:
    #     conn.execute(text("DROP TABLE IF EXISTS transaction_summary CASCADE"))
    #     conn.commit()
        
    # transactionModel.TransactionSummary.__table__.drop(engine, checkfirst=True)
    transactionModel.TransactionSummary.__table__.create(engine, checkfirst=True)

create_db_and_tables()

router = APIRouter(tags=["Transactions"])

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/transactions", response_model=TransactionSummaryShowSchema)
def create_transaction(req: TransactionSummaryCreate, db: Session = Depends(get_session)):
    # Validate payment_mode
    valid_payment_modes = ["CASH", "DEBIT / CREDIT CARD", "UPI", "CHEQUE", "CASHLESS"]
    if req.payment_mode not in valid_payment_modes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid payment mode. Must be one of: {', '.join(valid_payment_modes)}"
        )

    # Check if transaction_no already exists
    existing_transaction = db.exec(
        select(TransactionSummary).where(
            TransactionSummary.transaction_no == req.transaction_no
        )
    ).first()
    
    if existing_transaction:
        raise HTTPException(
            status_code=400,
            detail="Transaction number already exists"
        )

    # Create TransactionSummary instance
    db_transaction = TransactionSummary(
        patient_uhid=req.patient_uhid,
        patient_regno=req.patient_regno,
        patient_name=req.patient_name,
        admission_date=req.admission_date,
        transaction_purpose=req.transaction_purpose,
        amount=req.amount,
        payment_mode=req.payment_mode,
        payment_details=req.payment_details,
        transaction_date=req.transaction_date,
        transaction_time=req.transaction_time,
        transaction_no=req.transaction_no,
        created_by=req.created_by
    )

    # Save to database
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction

@router.get("/transactions", response_model=List[TransactionSummaryShowSchema])
def get_transactions(db: Session = Depends(get_session)):
    transactions = db.exec(select(TransactionSummary)).all()
    return transactions



@router.get('/transactions/patient/{uhid}', response_model=PatientDetailsSearchSchemaForTransaction)
def get_patient_for_transaction(uhid: str, db: Session = Depends(get_session)):

    # Step 1: Get latest registration for this UHID
    latest_patient = db.exec(
        select(PatientDetails)
        .where(PatientDetails.uhid == uhid)
        .order_by(PatientDetails.regno.desc())  # latest regno here found out
        .limit(1)
    ).first()

    if not latest_patient:
        raise HTTPException(status_code=404, detail=f"No registration found for UHID {uhid}")

    # Step 2: Ensure patient is IPD
    if latest_patient.patient_type != "IPD":
        raise HTTPException(
            status_code=400,
            detail=f"UHID {uhid} is not registered as IPD (found {latest_patient.patient_type}), directly generate a bill of it."
        )

    # Step 3: Return the most recent patient record
    return latest_patient



@router.get("/transactions/summary/{uhid}", response_model=List[AllTransactionSummaryShowSchema])
def get_all_transactions_by_uhid(uhid: str, db: Session = Depends(get_session)):
    transactions = db.exec(
        select(TransactionSummary).where(TransactionSummary.patient_uhid == uhid)
        .order_by(TransactionSummary.id.desc())
    ).all()
    if not transactions:
        raise HTTPException(status_code=404, detail=f"No transactions found for UHID {uhid}")
    return transactions


@router.put("/transactions/cancel/{transaction_no}", response_model=TransactionSummaryShowSchema)
def cancel_transaction(
    transaction_no: str,
    req: UpdateTransactionSchema,
    db: Session = Depends(get_session)
):
    txn = db.exec(
        select(TransactionSummary).where(TransactionSummary.transaction_no == transaction_no)
    ).first()

    if not txn:
        raise HTTPException(status_code=404, detail=f"Transaction {transaction_no} not found")

    if txn.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Transaction is already cancelled")

    txn.status = "cancelled"
    txn.cancelled_by = req.cancelled_by

    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


