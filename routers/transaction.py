from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, text
from models.patient_model import PatientDetails
from models.transaction_model import TransactionSummary
from schemas.transaction_schemas import TransactionSummaryCreate, PatientDetailsSearchSchemaForTransaction, TransactionSummaryShowSchema, AllTransactionSummaryShowSchema, UpdateTransactionSchema
from typing import List
from database import engine
import models.transaction_model as transactionModel


def create_db_and_tables():

    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS patientdetails CASCADE"))
        conn.commit()
        
    transactionModel.TransactionSummary.__table__.drop(engine, checkfirst=True)
    transactionModel.TransactionSummary.__table__.create(engine)

create_db_and_tables()

router = APIRouter(tags=["Transactions"])

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/transactions", response_model=TransactionSummaryShowSchema)
def create_transaction(req: TransactionSummaryCreate, db: Session = Depends(get_session)):
    # Validate payment_mode
    valid_payment_modes = ["CASH", "CARD", "UPI", "CHEQUE", "NEFT", "RTGS"]
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


# Fixed the route decorator and added missing uhid parameter
@router.get('/transactions/patient/{uhid}', response_model=PatientDetailsSearchSchemaForTransaction)
def get_patient_for_transaction(uhid: str, db: Session = Depends(get_session)):
    patient = db.exec(
        select(PatientDetails)
        .where(PatientDetails.uhid == uhid)
        .order_by(PatientDetails.regno.desc())  # Order by registration date descending
    ).first()  # Get only the first (most recent) record
    
    if not patient:
        raise HTTPException(status_code=404, detail=f"No patient found for UHID {uhid}")
    return patient



@router.get("/transactions/summary/{uhid}", response_model=List[AllTransactionSummaryShowSchema])
def get_all_transactions_by_uhid(uhid: str, db: Session = Depends(get_session)):
    transactions = db.exec(
        select(TransactionSummary).where(TransactionSummary.patient_uhid == uhid)
        .order_by(TransactionSummary.transaction_date.desc(), TransactionSummary.transaction_time.desc())
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


# # Additional useful routes for your billing system
# @router.get("/transactions/patient/{uhid}/regno/{regno}", response_model=List[TransactionSummary])
# def get_patient_transactions_by_visit(
#     uhid: str, 
#     regno: str, 
#     db: Session = Depends(get_session)
# ):
#     """
#     Get all transactions for a specific patient visit (UHID + Regno combination)
#     """
#     transactions = db.exec(
#         select(TransactionSummary).where(
#             TransactionSummary.patient_uhid == uhid,
#             TransactionSummary.patient_regno == regno
#         ).order_by(
#             TransactionSummary.transaction_date.desc(), 
#             TransactionSummary.transaction_time.desc()
#         )
#     ).all()
    
#     if not transactions:
#         raise HTTPException(
#             status_code=404,
#             detail=f"No transactions found for UHID {uhid} and Regno {regno}"
#         )
    
#     return transactions

# @router.get("/transactions/patient/{uhid}/latest", response_model=List[TransactionSummary])
# def get_patient_latest_visit_transactions(uhid: str, db: Session = Depends(get_session)):
#     """
#     Get all transactions for a patient's latest visit (most recent regno)
#     """
#     # First get the latest regno for this UHID
#     latest_patient = db.exec(
#         select(PatientDetails)
#         .where(PatientDetails.uhid == uhid)
#         .order_by(PatientDetails.regno.desc())
#     ).first()
    
#     if not latest_patient:
#         raise HTTPException(
#             status_code=404,
#             detail=f"No patient found with UHID: {uhid}"
#         )
    
#     # Get transactions for the latest visit
#     transactions = db.exec(
#         select(TransactionSummary).where(
#             TransactionSummary.patient_uhid == uhid,
#             TransactionSummary.patient_regno == latest_patient.regno
#         ).order_by(
#             TransactionSummary.transaction_date.desc(), 
#             TransactionSummary.transaction_time.desc()
#         )
#     ).all()
    
#     return transactions  # Return empty list if no transactions found

# @router.get("/transactions/{transaction_no}", response_model=TransactionSummary)
# def get_transaction_by_number(transaction_no: str, db: Session = Depends(get_session)):
#     """
#     Get a specific transaction by transaction number
#     """
#     transaction = db.exec(
#         select(TransactionSummary).where(
#             TransactionSummary.transaction_no == transaction_no
#         )
#     ).first()
    
#     if not transaction:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Transaction with number {transaction_no} not found"
#         )
    
#     return transaction
