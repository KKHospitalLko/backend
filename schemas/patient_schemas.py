from sqlmodel import SQLModel
from typing import Optional, List
from pydantic import field_validator, field_serializer
from datetime import datetime, timezone
import pytz
import re

class Address(SQLModel):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip: Optional[int] = None

    @field_validator('zip', mode='before')
    def validate_zip(cls, v):
        if v is None:
            return None
        if not isinstance(v, int):
            try:
                v = int(v)  # Convert string to int (e.g., "123456")
            except ValueError:
                raise ValueError("Zip code must be a number")
        if v < 0:
            raise ValueError("Zip code must not be negative")
        if v > 999999:
            raise ValueError("Zip code must not exceed 6 digits")
        if v < 10 and v != 0:  # Allow 0, but reject 1-9 (single digit)
            raise ValueError("Zip code must be at least 2 digits unless it is 0")
        return v

def get_current_ist_time():
    """Get current IST time reliably"""
    utc_now = datetime.now(timezone.utc)
    ist_tz = pytz.timezone('Asia/Kolkata')
    ist_time = utc_now.astimezone(ist_tz)
    return ist_time

class PatientDetailsCreateSchema(SQLModel):
    title: Optional[str] = None
    fullname: str
    sex: Optional[str] = None
    mobile: Optional[str] = None
    dateofreg: Optional[str] = None
    time: Optional[str] = None
    age: Optional[int] = None
    empanelment: Optional[str] = None
    bloodGroup: Optional[str] = None
    religion: str
    maritalStatus: str
    fatherHusband: str
    doctorIncharge: List[str]
    regAmount: int  # Required, non-optional
    localAddress: Address
    permanentAddress: Address
    registered_by: str

    @field_validator('mobile', mode='before')
    def validate_mobile(cls, v):
        if v is None or v.strip() == "":
            return None
        cleaned_mobile = re.sub(r'\D', '', v)
        if not re.match(r'^[6-9]\d{9}$', cleaned_mobile):
            raise ValueError("Mobile number must be a valid 10-digit number starting with 6-9")
        return cleaned_mobile

    @field_validator('regAmount', mode='before')
    def validate_reg_amount(cls, v):
        if v is None:
            raise ValueError("Registration amount is required")
        if not isinstance(v, int):
            try:
                v = int(v)  # Convert string to int (e.g., "1000")
            except ValueError:
                raise ValueError("Registration amount must be a number")
        if v < 0:
            raise ValueError("Registration amount must not be negative")
        if v > 9999999:
            raise ValueError("Registration amount must not exceed 7 digits")
        return v

    @field_validator('dateofreg', mode='before')
    def handle_invalid_date(cls, v):
        if v and v != "string":
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("dateofreg must be in YYYY-MM-DD format")
        return v or get_current_ist_time().strftime("%Y-%m-%d")

    @field_validator('time', mode='before')
    def handle_invalid_time(cls, v):
        if v and v != "string":
            try:
                datetime.strptime(v, "%I:%M:%S %p")
            except ValueError:
                try:
                    parsed_time = datetime.strptime(v, "%H:%M:%S")
                    return parsed_time.strftime("%I:%M:%S %p")
                except ValueError:
                    raise ValueError("time must be in HH:MM:SS (24-hour) or HH:MM:SS AM/PM (12-hour) format")
        return v or get_current_ist_time().strftime("%I:%M:%S %p")

class PatientDetailsUpdateSchema(PatientDetailsCreateSchema):
    title: Optional[str] = None
    fullname: Optional[str] = None
    sex: Optional[str] = None
    mobile: Optional[str] = None
    dateofreg: Optional[str] = None
    time: Optional[str] = None
    age: Optional[int] = None
    empanelment: Optional[str] = None
    bloodGroup: Optional[str] = None
    religion: Optional[str] = None
    maritalStatus: Optional[str] = None
    fatherHusband: Optional[str] = None
    doctorIncharge: Optional[List[str]] = None
    regAmount: Optional[int] = None  # Optional for updates
    localAddress: Optional[Address] = None
    permanentAddress: Optional[Address] = None
    registered_by: Optional[str] = None

    @field_validator('regAmount', mode='before')
    def validate_reg_amount(cls, v):
        if v is None:
            return None  # Allow None for updates
        if not isinstance(v, int):
            try:
                v = int(v)
            except ValueError:
                raise ValueError("Registration amount must be a number")
        if v < 0:
            raise ValueError("Registration amount must not be negative")
        if v > 9999999:
            raise ValueError("Registration amount must not exceed 7 digits")
        return v

class PatientDetailsResponseSchema(SQLModel):
    uhid: Optional[str] = None
    fullname: str
    mobile: Optional[str] = None
    regno: Optional[int] = None
    registered_by: str

    @field_serializer('regno')
    def serialize_regno(self, regno: Optional[int], _info):
        return f"{regno:04d}" if regno is not None else None

class PatientDetailsSearchResponseSchema(SQLModel):
    uhid: Optional[str] = None
    title: Optional[str] = None
    fullname: str
    sex: Optional[str] = None
    mobile: Optional[str] = None
    dateofreg: str
    regno: Optional[int] = None
    time: Optional[str] = None
    age: Optional[int] = None
    empanelment: Optional[str] = None
    bloodGroup: Optional[str] = None
    religion: str
    maritalStatus: str
    fatherHusband: str
    doctorIncharge: List[str]
    regAmount: int
    localAddress: Address
    permanentAddress: Address
    registered_by: str

    @field_serializer('regno')
    def serialize_regno(self, regno: Optional[int], _info):
        return f"{regno:04d}" if regno is not None else None