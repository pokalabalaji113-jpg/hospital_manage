from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date

import database_models
from database import SessionLocal, engine
from models import (
    PatientCreate, PatientResponse,
    DoctorCreate, DoctorResponse,
    AppointmentCreate, AppointmentResponse
)

# -------------------------------------------------
# Create Tables
# -------------------------------------------------
database_models.Base.metadata.create_all(bind=engine)

# -------------------------------------------------
# Create App
# -------------------------------------------------
app = FastAPI()

# -------------------------------------------------
# CORS (For Streamlit)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Database Dependency
# -------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =================================================
# ================= PATIENT APIs ==================
# =================================================

@app.get("/patients", response_model=list[PatientResponse])
def get_patients(db: Session = Depends(get_db)):
    return db.query(database_models.Patient).order_by(database_models.Patient.id).all()


@app.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient_by_id(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(database_models.Patient).filter(
        database_models.Patient.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient


@app.post("/patients")
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    new_patient = database_models.Patient(**patient.model_dump())
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return {"message": "Patient added successfully"}


@app.put("/patients/{patient_id}")
def update_patient(patient_id: int, patient: PatientCreate, db: Session = Depends(get_db)):

    db_patient = db.query(database_models.Patient).filter(
        database_models.Patient.id == patient_id
    ).first()

    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db_patient.name = patient.name
    db_patient.age = patient.age
    db_patient.gender = patient.gender
    db_patient.phone = patient.phone
    db_patient.address = patient.address
    db_patient.problem=patient.problem

    db.commit()
    db.refresh(db_patient)

    return {"message": "Patient updated successfully"}


@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):

    db_patient = db.query(database_models.Patient).filter(
        database_models.Patient.id == patient_id
    ).first()

    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(db_patient)
    db.commit()

    return {"message": "Patient deleted successfully"}

# =================================================
# ================= DOCTOR APIs ===================
# =================================================

@app.get("/doctors", response_model=list[DoctorResponse])
def get_doctors(db: Session = Depends(get_db)):
    return db.query(database_models.Doctor).order_by(database_models.Doctor.id).all()


@app.get("/doctors/{doctor_id}", response_model=DoctorResponse)
def get_doctor_by_id(doctor_id: int, db: Session = Depends(get_db)):

    doctor = db.query(database_models.Doctor).filter(
        database_models.Doctor.id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return doctor


@app.post("/doctors")
def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    new_doctor = database_models.Doctor(**doctor.model_dump())
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return {"message": "Doctor added successfully"}


@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: int, doctor: DoctorCreate, db: Session = Depends(get_db)):

    db_doctor = db.query(database_models.Doctor).filter(
        database_models.Doctor.id == doctor_id
    ).first()

    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    db_doctor.name = doctor.name
    db_doctor.specialization = doctor.specialization
    db_doctor.phone = doctor.phone

    db.commit()
    db.refresh(db_doctor)

    return {"message": "Doctor updated successfully"}


@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):

    db_doctor = db.query(database_models.Doctor).filter(
        database_models.Doctor.id == doctor_id
    ).first()

    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    db.delete(db_doctor)
    db.commit()

    return {"message": "Doctor deleted successfully"}

# =================================================
# ============== APPOINTMENT APIs =================
# =================================================

@app.get("/appointments", response_model=list[AppointmentResponse])
def get_appointments(db: Session = Depends(get_db)):
    return db.query(database_models.Appointment).order_by(database_models.Appointment.id).all()


@app.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
def get_appointment_by_id(appointment_id: int, db: Session = Depends(get_db)):

    appointment = db.query(database_models.Appointment).filter(
        database_models.Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return appointment


@app.post("/appointments")
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):

    # Check patient exists
    patient = db.query(database_models.Patient).filter(
        database_models.Patient.id == appointment.patient_id
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Check doctor exists
    doctor = db.query(database_models.Doctor).filter(
        database_models.Doctor.id == appointment.doctor_id
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Prevent past booking
    if appointment.appointment_date < date.today():
        raise HTTPException(status_code=400, detail="Cannot book past date")

    # Prevent double booking
    existing = db.query(database_models.Appointment).filter(
        database_models.Appointment.doctor_id == appointment.doctor_id,
        database_models.Appointment.appointment_date == appointment.appointment_date,
        database_models.Appointment.appointment_time == appointment.appointment_time
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Doctor already booked at this time")

    new_appointment = database_models.Appointment(**appointment.model_dump())
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return {"message": "Appointment booked successfully"}


@app.put("/appointments/{appointment_id}")
def update_appointment(appointment_id: int, appointment: AppointmentCreate, db: Session = Depends(get_db)):

    db_appointment = db.query(database_models.Appointment).filter(
        database_models.Appointment.id == appointment_id
    ).first()

    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    db_appointment.appointment_date = appointment.appointment_date
    db_appointment.appointment_time = appointment.appointment_time
    db_appointment.status = appointment.status
    db_appointment.patient_id = appointment.patient_id
    db_appointment.doctor_id = appointment.doctor_id

    db.commit()
    db.refresh(db_appointment)

    return {"message": "Appointment updated successfully"}


@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):

    db_appointment = db.query(database_models.Appointment).filter(
        database_models.Appointment.id == appointment_id
    ).first()

    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    db.delete(db_appointment)
    db.commit()

    return {"message": "Appointment deleted successfully"}