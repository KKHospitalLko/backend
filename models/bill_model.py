from typing import Optional
from decimal import Decimal
from sqlmodel import SQLModel, Field
from sqlalchemy import JSON


class FinalBillSummary(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    final_bill_no: str
    patient_uhid: str
    patient_regno: str
    patient_name: str
    age: str
    gender: str
    admission_date: str
    admission_time: str
    discharge_date: str
    discharge_time: str
    consultant_doctor: str
    room_type: str
    bed_no: str
    reg_amount: Optional[Decimal] = Field(default=None, decimal_places=2)
    charges_summary: Optional[list] = Field(default=None, sa_type=JSON)
    transaction_breakdown: Optional[list] = Field(default=None, sa_type=JSON)
    medication_discount: Optional[Decimal] = Field(default=None, decimal_places=2)
    room_service_discount: Optional[Decimal] = Field(default=None, decimal_places=2)
    consultancy_charges_discount: Optional[Decimal] = Field(default=None, decimal_places=2)
    total_charges: Optional[Decimal] = Field(default=None, decimal_places=2)
    total_discount: Optional[Decimal] = Field(default=None, decimal_places=2)
    net_amount: Optional[Decimal] = Field(default=None, decimal_places=2)
    total_paid: Optional[Decimal] = Field(default=None, decimal_places=2)
    balance: Optional[Decimal] = Field(default=None, decimal_places=2)
    created_by: str
    status: str = Field(default="ACTIVE", index=True, description="Bill status: ACTIVE or CANCELLED")
    cancelled_by: Optional[str] = None

    # class Config:
    #     json_encoders = {
    #         Decimal: lambda v: float(v)
    #     }
