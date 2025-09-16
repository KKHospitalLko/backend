from decimal import Decimal
from typing import List, Optional
from pydantic import field_serializer
from sqlmodel import Field, SQLModel


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
    patient_type: str
    sex: Optional[str] = None
    dateofreg: str
    regno: Optional[str] = None
    time: Optional[str] = None
    age: Optional[int] = None
    fatherHusband: str
    doctorIncharge: List[str]
    regAmount: int
    empanelment: str



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
    

class TotalDiscount(SQLModel):
    discount_type: str
    discount_percent: Optional[Decimal] = None
    discount_rupee: Optional[Decimal] = None

    @field_serializer("discount_rupee", when_used="json")
    def format_rupee(self, v: Optional[Decimal], _info):
        if v is None:
            return None
        return f"{v:.2f}"

    @field_serializer("discount_percent", when_used="json")
    def format_percent(self, v: Optional[Decimal], _info):
        if v is None:
            return None
        return f"{v:.2f}%"  # converts Decimal to string with %



class FinalBillSummaryCreate(SQLModel):
    final_bill_no: str
    patient_uhid: str
    patient_regno: str
    patient_name: str
    patient_type: str
    age: str
    gender: str
    admission_date: str
    admission_time: str
    discharge_date: str
    discharge_time: str
    consultant_doctor: str
    empanelment: str
    room_type: Optional[str] = None
    bed_no: Optional[str] = None
    reg_amount: Optional[Decimal] = None
    charges_summary: List[ChargesSummary] = Field(default_factory=list)
    transaction_breakdown: List[TransactionBreakdown] = Field(default_factory=list)
    total_charges: Optional[Decimal] = None
    total_discount: Optional[TotalDiscount] = None
    net_amount: Optional[Decimal] = None
    total_paid: Optional[Decimal] = None
    balance: Optional[Decimal] = None
    created_by: str




class FinalBillSummaryShowSchema(SQLModel):
    final_bill_no: str
    patient_uhid: str
    patient_regno: str
    patient_name: str
    patient_type: str
    age: str
    gender: str
    admission_date: str
    admission_time: str
    discharge_date: str
    discharge_time: str
    consultant_doctor: str
    empanelment: str
    room_type: str
    bed_no: str
    reg_amount: Optional[Decimal] = None
    charges_summary: Optional[List[ChargesSummary]] = None
    transaction_breakdown: Optional[List[TransactionBreakdown]] = None
    total_charges: Optional[Decimal] = None
    total_discount: Optional[TotalDiscount] = None
    net_amount: Optional[Decimal] = None
    total_paid: Optional[Decimal] = None
    balance: Optional[Decimal] = None
    created_by: str
    status: str
    cancelled_by: Optional[str] = None

    @field_serializer(
        "total_charges", "net_amount", "total_paid", "balance", "reg_amount",
        when_used="json"
    )
    def format_decimal(self, v: Decimal, _info):
        if v is None:
            return None
        return f"{v:.2f}"


class UpdateBillSchema(SQLModel):
    cancelled_by: str