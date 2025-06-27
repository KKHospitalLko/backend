from sqlmodel import SQLModel
from typing import Optional
from pydantic import field_validator, field_serializer
from datetime import datetime

class PatientDetailsCreateSchema(SQLModel):
    title: Optional[str] = None
    fullname: str
    department: str
    sex: Optional[str] = None
    mobile: Optional[int] = None
    dateofreg: Optional[str] = None

    @field_validator('title', mode='before')
    def handle_empty_title(cls, v):
        return None if v == "" else v

    @field_validator('mobile', mode='before')
    def handle_invalid_mobile(cls, v):
        return None if v == 0 else v

    @field_validator('dateofreg', mode='before')
    def handle_invalid_date(cls, v):
        if v and v != "string":
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("dateofreg must be in YYYY-MM-DD format")
        return v or datetime.now().strftime("%Y-%m-%d")

    @field_validator('fullname', 'department', mode='before')
    def check_non_empty(cls, v):
        if not v.strip():
            raise ValueError("Value cannot be empty")
        return v

class PatientDetailsUpdateSchema(PatientDetailsCreateSchema):
    title: Optional[str] = None
    fullname: Optional[str] = None
    department: Optional[str] = None
    sex: Optional[str] = None
    mobile: Optional[int] = None
    dateofreg: Optional[str] = None

class PatientDetailsResponseSchema(SQLModel):
    uhid: Optional[str] = None
    title: Optional[str] = None
    fullname: str
    department: str
    sex: Optional[str] = None
    mobile: Optional[int] = None
    dateofreg: str
    regno: Optional[int] = None

    @field_serializer('regno')
    def serialize_regno(self, regno: Optional[int], _info):
        return f"{regno:04d}" if regno is not None else None