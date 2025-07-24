from sqlmodel import SQLModel, Field
from typing import Optional, List
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
    empanelment: Optional[str] = None
    bloodGroup: Optional[str] = None
    religion: str
    maritalStatus: str
    fatherHusband: str
    doctorIncharge: Optional[List[str]] = Field(default=None, sa_type=JSON)
    regAmount: int
    localAddress: Optional[dict] = Field(default=None, sa_type=JSON)
    permanentAddress: Optional[dict] = Field(default=None, sa_type=JSON)
    registered_by: str