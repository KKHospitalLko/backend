from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, text
from models.bed_model import BedDetails
from models.patient_model import PatientDetails
from schemas.bed_schemas import BedDetailsResponseSchema, BedDetailsCreateSchema
from database import engine
from schemas.patient_schemas import PatientDetailsResponseSchema


router = APIRouter(tags=["Bed"])

# Create tables and initialize beds
def create_db_and_tables():

    # with engine.connect() as conn:
    #     conn.execute(text("DROP TABLE IF EXISTS beddetails CASCADE"))
    #     conn.commit()
        
    # BedDetails.__table__.drop(engine, checkfirst=True)
    BedDetails.__table__.create(engine, checkfirst=True)
    
    # Initialize departments and beds
    with Session(engine) as session:
        # Define departments and beds
        departments = [
    {"name": "Emergency - ground floor", "beds": ["E-1", "E-2", "E-3", "E-4", "E-5", "E-6", "E-7", "E-8", "E-9"]},
    {"name": "ICU - 3rd Floor", "beds": ["ICU-1", "ICU-2", "ICU-3", "ICU-4", "ICU-5", "ICU-6", "ICU-7", "ICU-8", "ICU-9"]},
    {"name": "NICU - 2nd Floor", "beds": ["NICU-1", "NICU-2", "NICU-3", "NICU-4", "NICU-5", "NICU-6", "NICU-7", "NICU-8"]},
    {"name": "HDU - 3rd Floor", "beds": ["HDU-301", "HDU-302", "HDU-303", "HDU-304", "HDU-305", "HDU-306", "HDU-307", "HDU-308"]},
    {"name": "Dialysis - Ground Floor", "beds": ["D-1", "D-2", "D-3", "D-4", "D-5"]},
    {"name": "Male Ward - Lower Ground Floor", "beds": ["MW-10", "MW-11", "MW-12", "MW-13", "MW-14", "MW-15", "MW-16", "MW-17"]},
    {"name": "Female Ward - Lower Ground Floor", "beds": ["FW-1", "FW-2", "FW-3", "FW-4", "FW-5", "FW-6", "FW-7", "FW-8"]},
    {"name": "General Ward - 2nd Floor", "beds": ["GW-206", "GW-207", "GW-208", "GW-209", "GW-210"]},
    {"name": "General Ward (AC) - 2nd Floor", "beds": ["GWAC-220", "GWAC-221", "GWAC-222", "GWAC-223"]},
    {"name": "Post-Op - 3rd Floor", "beds": ["PO-1", "PO-2", "PO-3", "PO-4", "PO-5", "PO-6", "PO-7", "PO-8"]},
    {"name": "Private - 1st Floor", "beds": ["P1-102", "P1-103", "P1-104", "P1-105", "P1-106 (Reserved)", "P1-107", "P1-108", "P1-109", "P1-110"]},
    {"name": "Semi-Private - 1st Floor", "beds": ["SP1-111 A", "SP1-111 B", "SP1-112 A", "SP1-112 B", "SP1-113 A", "SP1-113 B"]},
    {"name": "Semi-Private - 2nd Floor", "beds": ["SP2-201 A", "SP2-201 B", "SP2-202 A", "SP2-202 B", "SP2-203", "SP2-204", "SP2-205 A", "SP2-205 B",
                                                 "SP2-211 A", "SP2-211 B", "SP2-212 A", "SP2-212 B", "SP2-213 A", "SP2-213 B", "SP2-214 A", "SP2-214 B",
                                                 "SP2-215 A", "SP2-215 B", "SP2-216 A", "SP2-216 B"]},
    {"name": "Private - 2nd Floor", "beds": ["P2-217", "P2-218", "P2-219"]}
]
        for dept in departments:
            for bed_number in dept["beds"]:
                if not session.exec(select(BedDetails).where(BedDetails.bed_number == bed_number)).first():
                    bed = BedDetails(
                        department=dept["name"],
                        bed_number=bed_number,
                        patient_name="",
                        uhid=None,
                        status="available"
                    )
                    session.add(bed)
        session.commit()

create_db_and_tables()


# Get a session
def get_session():
    with Session(engine) as session:
        yield session



@router.post('/bed_allotment', response_model=BedDetailsResponseSchema)
def create_bed(req: BedDetailsCreateSchema, db: Session = Depends(get_session)):
    bed = db.exec(select(BedDetails).where(BedDetails.bed_number == req.bed_number)).first()
    dept = db.exec(select(BedDetails).where(BedDetails.department == req.department)).first()
    uhidF= db.exec(select(BedDetails).where(BedDetails.uhid == req.uhid)).first()


    if not bed:
        raise HTTPException(status_code=404, detail=f"Bed {req.bed_number} not found")
    if bed.status == "occupied":
        raise HTTPException(status_code=400, detail=f"Bed {req.bed_number} is already occupied")
    
    if not dept:
        raise HTTPException(status_code=404, detail=f"Department {req.department} not found")
    
    if uhidF:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= f"Bed is alredy alloted to UHID {req.uhid}")
    
    # Update existing bed
    bed.uhid = req.uhid
    bed.patient_name = req.patient_name
    bed.department = req.department
    bed.status = "occupied"  # Automatically set to occupied
    db.add(bed)
    db.commit()
    db.refresh(bed)
    return bed



@router.get('/beds', response_model=List[BedDetailsResponseSchema])
def get_all_beds(db: Session = Depends(get_session)):
    beds = db.exec(select(BedDetails)).all()
    return [BedDetailsResponseSchema.model_validate(bed) for bed in beds]




@router.get('/beds/available', response_model=dict)
def get_available_beds(db: Session = Depends(get_session)):
    departments = [
  "Emergency - ground floor",
  "ICU - 3rd Floor",
  "NICU - 2nd Floor",
  "HDU - 3rd Floor",
  "Dialysis - Ground Floor",
  "Male Ward - Lower Ground Floor",
  "Female Ward - Lower Ground Floor",
  "General Ward - 2nd Floor",
  "General Ward (AC) - 2nd Floor",
  "Post-Op - 3rd Floor",
  "Private - 1st Floor",
  "Semi-Private - 1st Floor",
  "Semi-Private - 2nd Floor",
  "Private - 2nd Floor",
];
    available_beds = {}
    for dept in departments:
        beds = db.exec(
            select(BedDetails).where(BedDetails.department == dept, BedDetails.status == "available")
        ).all()
        available_beds[dept] = [bed.bed_number for bed in beds]
    return {"available_beds": available_beds}


@router.delete('/bed/{bed_number}')
def delete_bed(bed_number: str, db: Session = Depends(get_session)):
    bed = db.exec(select(BedDetails).where(BedDetails.bed_number == bed_number)).first()
    if not bed:
        raise HTTPException(status_code=404, detail=f"Bed {bed_number} not found")

    # Reset bed to available instead of deleting
    bed.uhid = None
    bed.patient_name = ""
    bed.status = "available"
    db.add(bed)
    db.commit()
    return {"message": f"Bed {bed_number} reset and marked as available"}


@router.put('/bed/shift', response_model=BedDetailsResponseSchema)
def shift_bed(req: BedDetailsCreateSchema, db: Session = Depends(get_session)):
    # Find the source bed (where patient is currently, identified by uhid)
    if not req.uhid:
        raise HTTPException(status_code=400, detail="UHID is required to identify the source bed")
    source_bed = db.exec(select(BedDetails).where(BedDetails.uhid == req.uhid, BedDetails.status == "occupied")).first()
    if not source_bed:
        raise HTTPException(status_code=404, detail=f"No occupied bed found for UHID {req.uhid}")
    # Find the target bed (new bed_number)
    target_bed = db.exec(select(BedDetails).where(BedDetails.bed_number == req.bed_number)).first()
    if not target_bed:
        raise HTTPException(status_code=404, detail=f"Target bed {req.bed_number} not found")
    if target_bed.status == "occupied":
        raise HTTPException(status_code=400, detail=f"Target bed {req.bed_number} is already occupied")
    # Update source bed to available
    source_bed.uhid = None
    source_bed.patient_name = ""
    source_bed.status = "available"
    db.add(source_bed)
    # Update target bed to occupied with new details
    target_bed.uhid = req.uhid
    target_bed.patient_name = req.patient_name
    target_bed.department = req.department
    target_bed.status = "occupied"
    db.add(target_bed)
    db.commit()
    db.refresh(target_bed)
    return target_bed



@router.get('/beds/patient/{uhid}', response_model=PatientDetailsResponseSchema)
def get_patient_by_uhid_for_bed(uhid: str, db: Session = Depends(get_session)):
    patient = db.exec(
        select(PatientDetails)
        .where(PatientDetails.uhid == uhid)
        .order_by(PatientDetails.regno.desc())  # Order by registration date descending
    ).first()  # Get only the first (most recent) record
    
    if not patient:
        raise HTTPException(status_code=404, detail=f"No patient found for UHID {uhid}")
    return patient




