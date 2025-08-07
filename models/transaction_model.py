from sqlmodel import SQLModel, Field, JSON
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal


class TransactionSummary(SQLModel, table=True):
    __tablename__ = "transaction_summary"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_uhid: str = Field(foreign_key="patientdetails.uhid", index=True)
    patient_regno: str = Field(index=True)
    patient_name: str
    admission_date: str
    transaction_purpose: str
    amount: Optional[Decimal] = Field(default=None, decimal_places=2)
    payment_mode: str
    payment_details: Optional[dict] = Field(default=None, sa_type=JSON)
    transaction_date: str
    transaction_time: str
    transaction_no: str = Field(unique=True)
    created_by: str
    status: str = Field(default="ACTIVE", index=True, description="Transaction status: ACTIVE or CANCELLED")
    cancelled_by: Optional[str] = None
