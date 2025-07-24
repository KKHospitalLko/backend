from sqlmodel import SQLModel, Field
from typing import Optional

class BedDetails(SQLModel, table=True):
    bed_id: Optional[int] = Field(default=None, primary_key=True)
    uhid: Optional[str] = Field(default=None, index=True)  # No relationship
    patient_name: str
    department: str
    bed_number: str = Field(unique=True)
    status: str = Field(default="available")  # Tracks "available" or "occupied"