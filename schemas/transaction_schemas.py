from typing import Optional
from decimal import Decimal
from pydantic import Field, field_validator
from datetime import datetime
import re
from sqlmodel import SQLModel

class TransactionSummaryCreate(SQLModel):
    patient_uhid: str
    patient_regno: str
    patient_name: str
    admission_date: str
    transaction_purpose: str
    amount: Optional[Decimal] = None  # Made optional with automatic conversion
    payment_mode: str
    payment_details: Optional[dict] = None
    transaction_date: str
    transaction_time: str
    transaction_no: str
    created_by: str

    @field_validator('amount', mode='before')
    def convert_amount_to_decimal(cls, v):
        """Convert any number (int, float, str) to Decimal"""
        if v is None:
            raise ValueError("Amount is required")
        
        # Convert to Decimal regardless of input type
        try:
            decimal_value = Decimal(str(v))
        except (ValueError, TypeError):
            raise ValueError("Amount must be a valid number")
        
        # Validate the decimal value
        if decimal_value < 0:
            raise ValueError("Amount must be positive")
        if decimal_value > Decimal('9999999.99'):
            raise ValueError("Amount too large")
        
        return decimal_value

    @field_validator('transaction_date')
    def validate_transaction_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Transaction date must be in YYYY-MM-DD format")
        return v

    @field_validator('transaction_time')
    def validate_transaction_time(cls, v):
        try:
            # Check if it's in 24-hour format
            datetime.strptime(v, "%H:%M:%S")
            return v
        except ValueError:
            try:
                # Check if it's in 12-hour format with AM/PM
                datetime.strptime(v, "%I:%M:%S %p")
                return v  # <-- No conversion, return as-is
            except ValueError:
                raise ValueError("Time must be in HH:MM:SS (24-hour) or HH:MM:SS AM/PM (12-hour) format")


    @field_validator('patient_regno')
    def validate_regno_format(cls, v):
        if not re.match(r'^\d{3}$', v):
            raise ValueError("Regno must be 3 digits (001 format)")
        return v


    @field_validator('payment_mode')
    def validate_payment_mode(cls, v):
        valid_modes = ["CASH", "DEBIT / CREDIT CARD", "UPI", "CHEQUE", "CASHLESS"]
        if v not in valid_modes:
            raise ValueError(f"Payment mode must be one of: {', '.join(valid_modes)}")
        return v



    @field_validator('admission_date')
    def validate_admission_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Admission date must be in YYYY-MM-DD format")
        return v
    
    @field_validator('patient_uhid', mode='before')
    def validate_uhid(cls, v):
        if v is not None:  # Only validate if uhid is provided
            if v.startswith('-'):
                raise ValueError("UHID cannot be negative")
            if not v.isdigit() or len(v) != 8:
                raise ValueError("UHID must be exactly 8 digits")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "patient_uhid": "25070001",
                "patient_regno": "003",
                "patient_name": "John Doe",
                "admission_date": "2025-07-31",
                "transaction_purpose": "ADVANCE",
                "amount": 5000.00,  # Can be int, float, or string
                "payment_mode": "CASH",
                "payment_details": {
                    "bankname": "State Bank of India",
                    "banknumber": "XXXX-XXXX-XXXX-1234",
                    "dateofcheque": "2025-07-31"
                },
                "transaction_date": "2025-07-31",
                "transaction_time": "15:30:00",
                "transaction_no": "TXN202507310001",
                "created_by": "Dr. Smith"
            }
        }


class TransactionSummaryShowSchema(SQLModel):
    patient_uhid: str
    patient_regno: str
    patient_name: str
    admission_date: str
    transaction_purpose: str
    amount: Optional[Decimal] = None  # Made optional with automatic conversion
    payment_mode: str
    payment_details: Optional[dict] = None
    transaction_date: str
    transaction_time: str
    transaction_no: str
    created_by: str
    status: str 
    cancelled_by: Optional[str] = None


class AllTransactionSummaryShowSchema(SQLModel):
    patient_uhid: str
    patient_regno: str
    patient_name: str
    admission_date: str
    transaction_purpose: str
    amount: Optional[Decimal] = None
    payment_mode: str
    payment_details: Optional[dict] = None
    transaction_date: str
    transaction_time: str
    transaction_no: str
    created_by: str
    status: str 
    cancelled_by: Optional[str] = None



class PatientDetailsSearchSchemaForTransaction(SQLModel):
    fullname: str
    dateofreg: str
    regno: Optional[str] = None
    empanelment: str

class UpdateTransactionSchema(SQLModel):
    cancelled_by: str