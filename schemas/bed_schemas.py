from sqlmodel import SQLModel
from typing import Optional
from pydantic import field_validator

class BedDetailsCreateSchema(SQLModel):
    uhid: Optional[str] = None
    patient_name: str
    department: str
    bed_number: str

    @field_validator('patient_name', 'department', 'bed_number', mode='before')
    def check_non_empty(cls, v):
        if not v.strip():
            raise ValueError("Value cannot be empty")
        return v

    @field_validator('uhid', mode='before')
    def validate_uhid(cls, v):
        if v is not None:  # Only validate if uhid is provided
            if v.startswith('-'):
                raise ValueError("UHID cannot be negative")
            if not v.isdigit() or len(v) != 8:
                raise ValueError("UHID must be exactly 8 digits")
        return v

class BedDetailsResponseSchema(SQLModel):
    bed_id: Optional[int] = None
    uhid: Optional[str] = None
    patient_name: str
    department: str
    bed_number: str
    status: str