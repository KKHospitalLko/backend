from sqlmodel import SQLModel

class PatientDetailsSchema(SQLModel):
    fullname: str
    department: str

