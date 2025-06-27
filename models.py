from sqlmodel import SQLModel, Field
from typing import Optional

class PatientDetails(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uhid: Optional[str] = Field(default=None, index=True)  # No unique constraint
    title: Optional[str] = None
    fullname: str
    department: str
    sex: Optional[str] = None
    mobile: Optional[int] = None
    dateofreg: str
    regno: Optional[int] = None