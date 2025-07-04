from sqlmodel import SQLModel
from typing import Optional, List
from pydantic import field_validator, field_serializer
from datetime import datetime

class Address(SQLModel):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip: Optional[int] = None
    # email: Optional[str] = None

    # @field_validator('email', mode='before')
    # def handle_empty_email(cls, v):
    #     return None if v == "" else v

    @field_validator('address', 'city', 'state', 'country', mode='before')
    def check_non_empty(cls, v):
        return None if not v or v.strip() == "" else v

    @field_validator('zip', mode='before')
    def handle_invalid_zip(cls, v):
        return None if v == 0 else v

class PatientDetailsCreateSchema(SQLModel):
    title: Optional[str] = None
    fullname: str
    sex: Optional[str] = None
    mobile: Optional[int] = None
    dateofreg: Optional[str] = None
    time: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    empanelment: Optional[str] = None
    bloodGroup: Optional[str] = None
    religion: str
    intimationOrExtension: str
    maritalStatus: str
    fatherHusband: str
    doctorIncharge: List[str]
    regAmount: int
    localAddress: Address
    permanentAddress: Address

    @field_validator('title', 'occupation', 'empanelment', 'bloodGroup', mode='before')
    def handle_empty_string(cls, v):
        return None if v == "" else v

    @field_validator('mobile', 'age', mode='before')
    def handle_invalid_number(cls, v):
        return None if v == 0 else v

    @field_validator('dateofreg', mode='before')
    def handle_invalid_date(cls, v):
        if v and v != "string":
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("dateofreg must be in YYYY-MM-DD format")
        return v or datetime.now().strftime("%Y-%m-%d")

    @field_validator('time', mode='before')
    def handle_invalid_time(cls, v):
        if v and v != "string":
            try:
                datetime.strptime(v, "%H:%M:%S")
            except ValueError:
                raise ValueError("time must be in HH:MM:SS format")
        return v or datetime.now().strftime("%H:%M:%S")

    @field_validator('fullname', 'religion', 'intimationOrExtension', 'maritalStatus', 'fatherHusband', mode='before')
    def check_non_empty(cls, v):
        if not v.strip():
            raise ValueError("Value cannot be empty")
        return v

    @field_validator('doctorIncharge', mode='before')
    def check_non_empty_doctorIncharge(cls, v):
        if not v or not all(s.strip() for s in v):
            raise ValueError("doctorIncharge list cannot be empty or contain empty strings")
        return v

class PatientDetailsUpdateSchema(PatientDetailsCreateSchema):
    title: Optional[str] = None
    fullname: Optional[str] = None
    sex: Optional[str] = None
    mobile: Optional[int] = None
    dateofreg: Optional[str] = None
    time: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    empanelment: Optional[str] = None
    bloodGroup: Optional[str] = None
    religion: Optional[str] = None
    intimationOrExtension: Optional[str] = None
    maritalStatus: Optional[str] = None
    fatherHusband: Optional[str] = None
    doctorIncharge: Optional[List[str]] = None
    regAmount: Optional[int] = None
    localAddress: Optional[Address] = None
    permanentAddress: Optional[Address] = None

class PatientDetailsResponseSchema(SQLModel):
    uhid: Optional[str] = None
    title: Optional[str] = None
    fullname: str
    sex: Optional[str] = None
    mobile: Optional[int] = None
    dateofreg: str
    regno: Optional[int] = None
    time: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    empanelment: Optional[str] = None
    bloodGroup: Optional[str] = None
    religion: str
    intimationOrExtension: str
    maritalStatus: str
    fatherHusband: str
    doctorIncharge: List[str]
    regAmount: int
    localAddress: Address
    permanentAddress: Address

    @field_serializer('regno')
    def serialize_regno(self, regno: Optional[int], _info):
        return f"{regno:04d}" if regno is not None else None