from pydantic import BaseModel
from datetime import date, time

# ---------------- PATIENT ----------------
class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    phone: str
    address: str
    problem:str


class PatientResponse(PatientCreate):
    id: int

    class Config:
        from_attributes = True


# ---------------- DOCTOR ----------------
class DoctorCreate(BaseModel):
    name: str
    specialization: str
    phone: str


class DoctorResponse(DoctorCreate):
    id: int

    class Config:
        from_attributes = True


# ---------------- APPOINTMENT ----------------
class AppointmentCreate(BaseModel):
    appointment_date: date
    appointment_time: time
    status: str
    patient_id: int
    doctor_id: int


class AppointmentResponse(AppointmentCreate):
    id: int

    class Config:
        from_attributes = True