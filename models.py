from sqlmodel import SQLModel, Field
from typing import Optional
from sqlalchemy import JSON

class PatientDetails(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uhid: Optional[str] = Field(default=None, index=True)  # No unique constraint
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
    doctorIncharge: Optional[list[str]] = Field(default=None, sa_type=JSON)
    regAmount: int
    localAddress: Optional[dict] = Field(default=None, sa_type=JSON)
    permanentAddress: Optional[dict] = Field(default=None, sa_type=JSON)