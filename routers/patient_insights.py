from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from sqlmodel import Session, func, select
import models.patient_model as patient_model
import schemas.patient_schemas as patient_schemas
from database import engine
from models.bill_model import FinalBillSummary



router = APIRouter(tags=["Patient_Insights"])


def get_session():
    with Session(engine) as session:
        yield session



@router.get('/patients/count_and_graph')
def get_today_patient_counts(db: Session = Depends(get_session)):
    today_date = datetime.now().strftime("%Y-%m-%d")

    # --- Patient counts for today ---
    patient_types = ["OPD", "IPD", "DAYCARE"]
    today_counts = {}
    for p_type in patient_types:
        query = select(func.count()).where(
            patient_model.PatientDetails.dateofreg == today_date,
            patient_model.PatientDetails.patient_type == p_type
        )
        count = db.exec(query).one()
        today_counts[p_type] = count

    # --- Discharge count for today ---
    discharge_query = select(func.count()).where(
        FinalBillSummary.discharge_date == today_date
    )
    discharge_count = db.exec(discharge_query).one()

    # --- Graph data for last 30 days ---
    graph = {
        "OPD": {"dates_x_axis": [], "dates_y_axis": []},
        "IPD": {"dates_x_axis": [], "dates_y_axis": []},
        "DAYCARE": {"dates_x_axis": [], "dates_y_axis": []},
        "DISCHARGED": {"dates_x_axis": [], "dates_y_axis": []}
    }

    for i in range(30):
        day = datetime.now() - timedelta(days=29 - i)  # last 30 days
        day_str = day.strftime("%Y-%m-%d")

        for p_type in patient_types:
            query = select(func.count()).where(
                patient_model.PatientDetails.dateofreg == day_str,
                patient_model.PatientDetails.patient_type == p_type
            )
            count = db.exec(query).one()
            graph[p_type]["dates_x_axis"].append(day_str)
            graph[p_type]["dates_y_axis"].append(count)

        # Discharge count for this day
        discharge_query = select(func.count()).where(
            FinalBillSummary.discharge_date == day_str
        )
        discharge_count_day = db.exec(discharge_query).one()
        graph["DISCHARGED"]["dates_x_axis"].append(day_str)
        graph["DISCHARGED"]["dates_y_axis"].append(discharge_count_day)

    return {
        "count": {
            "date": today_date,
            "total_OPD": today_counts["OPD"],
            "total_IPD": today_counts["IPD"],
            "total_DAYCARE": today_counts["DAYCARE"],
            "total_Discharged": discharge_count
        },
        "graph": graph
    }





@router.get("/patients/filter", response_model=list[patient_schemas.PatientFilterSchema])
def filter_patients(
    patient_type: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    doctor_wise: Optional[str] = Query(None),
    empanelment: Optional[str] = Query(None),
    db: Session = Depends(get_session)
):
    query = (
        select(
            patient_model.PatientDetails,
            FinalBillSummary.discharge_date,
            FinalBillSummary.discharge_time
        )
        .outerjoin(
            FinalBillSummary,
            (FinalBillSummary.patient_uhid == patient_model.PatientDetails.uhid) &
            (FinalBillSummary.patient_regno == patient_model.PatientDetails.regno) &
            (FinalBillSummary.status != "CANCELLED")    # ✅ ignore cancelled discharges
        )
    )

    if patient_type:
        query = query.where(patient_model.PatientDetails.patient_type == patient_type)

    if date_from:
        query = query.where(patient_model.PatientDetails.dateofreg >= date_from)

    if date_to:
        query = query.where(patient_model.PatientDetails.dateofreg <= date_to)

    if doctor_wise and doctor_wise != "All":
        query = query.where(
            patient_model.PatientDetails.doctorIncharge.ilike(f'%{doctor_wise}%')
        )

    if empanelment:
        query = query.where(patient_model.PatientDetails.empanelment == empanelment)

    query = query.order_by(patient_model.PatientDetails.id.desc())

    result = db.exec(query).all()

    if not result:
        raise HTTPException(status_code=404, detail="No patients found with given filters")

    # Map discharge values
    patients = []
    for patient, dischargedate, dischargetime in result:
        p = patient.model_dump()
        p["dischargedate"] = dischargedate
        p["dischargetime"] = dischargetime
        patients.append(p)

    return patients
