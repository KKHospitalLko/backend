from sqlmodel import SQLModel
from typing import Optional, List
from pydantic import field_validator, field_serializer
from datetime import datetime, timezone
import pytz


class Address(SQLModel):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip: Optional[int] = None

    # @field_validator('address', 'city', 'state', 'country', mode='before')
    # def check_non_empty(cls, v):
    #     return None if not v or v.strip() == "" else v

    # @field_validator('zip', mode='before')
    # def handle_invalid_zip(cls, v):
    #     return None if v == 0 else v


# Helper function for IST time
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
    mobile: Optional[int] = None
    dateofreg: Optional[str] = None
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
    registered_by: str  # Required field

    # @field_validator('title', 'empanelment', 'bloodGroup', 'registered_by', mode='before')
    # def handle_empty_string(cls, v):
    #     if not v or v.strip() == "":
    #         raise ValueError(f"registered_by cannot be empty")
    #     return v

    # @field_validator('mobile', 'age', mode='before')
    # def handle_invalid_number(cls, v):
    #     return None if v == 0 else v

    @field_validator('dateofreg', mode='before')
    def handle_invalid_date(cls, v):
        if v and v != "string":
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("dateofreg must be in YYYY-MM-DD format")
        # Fix: Use IST time instead of system time
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
        # Fix: Use IST time instead of system time
        return v or get_current_ist_time().strftime("%I:%M:%S %p")


class PatientDetailsUpdateSchema(PatientDetailsCreateSchema):
    title: Optional[str] = None
    fullname: Optional[str] = None
    sex: Optional[str] = None
    mobile: Optional[int] = None
    dateofreg: Optional[str] = None
    time: Optional[str] = None
    age: Optional[int] = None
    empanelment: Optional[str] = None
    bloodGroup: Optional[str] = None
    religion: Optional[str] = None
    maritalStatus: Optional[str] = None
    fatherHusband: Optional[str] = None
    doctorIncharge: Optional[List[str]] = None
    regAmount: Optional[int] = None
    localAddress: Optional[Address] = None
    permanentAddress: Optional[Address] = None
    registered_by: Optional[str] = None  # Optional for updates to preserve existing value


class PatientDetailsResponseSchema(SQLModel):
    uhid: Optional[str] = None
    fullname: str
    mobile: Optional[int] = None
    regno: Optional[int] = None
    registered_by: str  # Required field

    @field_serializer('regno')
    def serialize_regno(self, regno: Optional[int], _info):
        return f"{regno:04d}" if regno is not None else None


class PatientDetailsSearchResponseSchema(SQLModel):
    uhid: Optional[str] = None
    title: Optional[str] = None
    fullname: str
    sex: Optional[str] = None
    mobile: Optional[int] = None
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
    registered_by: str  # Required field

    @field_serializer('regno')
    def serialize_regno(self, regno: Optional[int], _info):
        return f"{regno:04d}" if regno is not None else None
