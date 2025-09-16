from sqlmodel import SQLModel, Field, JSON, Index
from typing import Optional
from decimal import Decimal
from enum import Enum


class TransactionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"


class TransactionSummary(SQLModel, table=True):
    __tablename__ = "transaction_summary"
    __table_args__ = (
        Index("idx_patient_visit", "patient_uhid", "patient_regno"),
        Index("idx_transaction_no", "transaction_no", unique=True),
        Index("idx_transaction_date", "transaction_date"),
        Index("idx_status", "status"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    patient_uhid: str = Field(index=True)
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

    status: str = Field(
        default="ACTIVE",
        index=True,
        description="Transaction status: ACTIVE or CANCELLED"
    )
    cancelled_by: Optional[str] = None