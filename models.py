from sqlmodel import SQLModel, Field

class PatientDetails(SQLModel, table=True):
      uhid: int | None = Field(default=None, primary_key=True)
      fullname: str
      department: str