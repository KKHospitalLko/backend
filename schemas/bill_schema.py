from decimal import Decimal
from typing import List, Optional
from pydantic import field_serializer
from sqlmodel import Field, SQLModel
# from models.bill_model import ChargesSummary, TransactionBreakdown


# fot giving data to frontend from all tables

class AllTransactionSummaryShowSchemaForBill(SQLModel):
    amount: Optional[Decimal] = None
    transaction_date: str
    transaction_no: str

class BedDetailsShowSchemaForBill(SQLModel):
    department: str
    bed_number: str

class PatientDetailsShowSchemaForBill(SQLModel):
    uhid: Optional[str] = None
    title: Optional[str] = None
    fullname: str
    sex: Optional[str] = None
    dateofreg: str
    regno: Optional[str] = None
    time: Optional[str] = None
    age: Optional[int] = None
    fatherHusband: str
    doctorIncharge: List[str]
    regAmount: int



# for post route

class ChargesSummary(SQLModel):
    particulars: str
    quantity: Optional[int] = None
    rate: Optional[Decimal] = None
    amount: Optional[Decimal] = None

    @field_serializer("rate", "amount", when_used="json")
    def format_decimal(self, v: Decimal, _info):
        if v is None:
            return None
        return f"{v:.2f}"   # always 2 decimal places as string


class TransactionBreakdown(SQLModel):
    date: str
    transaction_no: str
    amount: Optional[Decimal] = None

    @field_serializer("amount", when_used="json")
    def format_decimal(self, v: Decimal, _info):
        if v is None:
            return None
        return f"{v:.2f}"

class FinalBillSummaryCreate(SQLModel):
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
    reg_amount: Optional[Decimal] = None
    charges_summary: Optional[List[ChargesSummary]] = None
    transaction_breakdown: Optional[List[TransactionBreakdown]] = None
    medication_discount: Optional[Decimal] = None
    room_service_discount: Optional[Decimal] = None
    consultancy_charges_discount: Optional[Decimal] = None
    total_charges: Optional[Decimal] = None
    total_discount: Optional[Decimal] = None
    net_amount: Optional[Decimal] = None
    total_paid: Optional[Decimal] = None
    balance: Optional[Decimal] = None
    created_by: str


    # class Config:
    #     json_encoders = {
    #         Decimal: lambda v: float(v)
    #     }


class FinalBillSummaryShowSchema(SQLModel):
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
    reg_amount: Optional[Decimal] = None
    charges_summary: Optional[List[ChargesSummary]] = None
    transaction_breakdown: Optional[List[TransactionBreakdown]] = None
    medication_discount: Optional[Decimal] = None
    room_service_discount: Optional[Decimal] = None
    consultancy_charges_discount: Optional[Decimal] = None
    total_charges: Optional[Decimal] = None
    total_discount: Optional[Decimal] = None
    net_amount: Optional[Decimal] = None
    total_paid: Optional[Decimal] = None
    balance: Optional[Decimal] = None
    created_by: str
    status: str
    cancelled_by: Optional[str] = None

    @field_serializer(
        "medication_discount", "room_service_discount", 
        "consultancy_charges_discount", "total_charges", 
        "total_discount", "net_amount", "total_paid", "balance", "reg_amount",
        when_used="json"
    )
    def format_decimal(self, v: Decimal, _info):
        if v is None:
            return None
        return f"{v:.2f}"


class UpdateBillSchema(SQLModel):
    cancelled_by: str