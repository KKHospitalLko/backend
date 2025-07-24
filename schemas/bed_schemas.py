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

class BedDetailsResponseSchema(SQLModel):
    bed_id: Optional[int] = None
    uhid: Optional[str] = None
    patient_name: str
    department: str
    bed_number: str
    status: str