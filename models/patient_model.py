from sqlmodel import SQLModel, Field
from typing import Optional, List
from sqlalchemy import JSON

class PatientDetails(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uhid: Optional[str] = Field(default=None, index=True) 
    adhaar_no: Optional[str] = Field(default=None, index=True)
    title: Optional[str] = None
    fullname: str
    sex: Optional[str] = None
    mobile: Optional[str] = None
    dateofreg: str
    regno: Optional[str] = None
    time: Optional[str] = None
    age: Optional[int] = None
    patient_type: str #type of patient
    empanelment: Optional[str] = None
    # bloodGroup: Optional[str] = None
    religion: str
    maritalStatus: str
    fatherHusband: str
    doctorIncharge: Optional[List[str]] = Field(default=None, sa_type=JSON)
    regAmount: int
    localAddress: Optional[dict] = Field(default=None, sa_type=JSON)
    permanentAddress: Optional[dict] = Field(default=None, sa_type=JSON)
    registered_by: str