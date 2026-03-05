import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Hospital Patient Management System",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================
st.markdown("""
<style>
.main-title {
    font-size: 38px;
    font-weight: bold;
    text-align: center;
    color: #2E86C1;
    margin-bottom: 20px;
}

.dashboard-card {
    background-color: #1f2937;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    color: white;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
}

.card-title {
    font-size: 18px;
    color: #9CA3AF;
}

.card-value {
    font-size: 32px;
    font-weight: bold;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("🏥 Hospital Patient Management System")
menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Patients", "Doctors", "Appointments"]
)

# =====================================================
# DASHBOARD
# =====================================================
if menu == "Dashboard":
    st.markdown('<div class="main-title">Hospital Patient Management System</div>', unsafe_allow_html=True)

    try:
        patients = requests.get(f"{API_URL}/patients").json()
        doctors = requests.get(f"{API_URL}/doctors").json()
        appointments = requests.get(f"{API_URL}/appointments").json()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-title">Total Patients</div>
                <div class="card-value">{len(patients)}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-title">Total Doctors</div>
                <div class="card-value">{len(doctors)}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-title">Total Appointments</div>
                <div class="card-value">{len(appointments)}</div>
            </div>
            """, unsafe_allow_html=True)

    except:
        st.error("Backend not running")

# =====================================================
# GENERIC CRUD FUNCTION
# =====================================================
def crud_section(title, endpoint, fields):
    st.title(title)
    tabs = st.tabs(["View All", "Get By ID", "Add", "Update", "Delete"])

    # VIEW ALL
    with tabs[0]:
        res = requests.get(f"{API_URL}/{endpoint}")
        if res.ok:
            st.dataframe(pd.DataFrame(res.json()), use_container_width=True)
        else:
            st.error("Error fetching data")

    # GET BY ID
    with tabs[1]:
        item_id = st.number_input("Enter ID", min_value=1, key=f"get_{endpoint}")
        if st.button("Fetch", key=f"fetch_{endpoint}"):
            res = requests.get(f"{API_URL}/{endpoint}/{item_id}")
            if res.ok:
                data = res.json()
                st.success("Record Found ✅")
                st.json(data)
            else:
                st.error("Not Found ❌")

    # ADD
    with tabs[2]:
        payload = {}

        for field in fields:
            if field in ["age", "patient_id", "doctor_id"]:
                payload[field] = st.number_input(field.capitalize(), min_value=0, key=f"add_{endpoint}_{field}")

            elif field in ["gender", "status"]:
                options = ["Male", "Female", "Other"] if field == "gender" else ["Scheduled", "Completed", "Cancelled"]
                payload[field] = st.selectbox(field.capitalize(), options, key=f"add_{endpoint}_{field}")

            elif field == "appointment_date":
                date_val = st.date_input("Appointment Date")
                payload[field] = date_val.strftime("%Y-%m-%d")

            elif field == "appointment_time":
                time_val = st.time_input("Appointment Time")
                payload[field] = time_val.strftime("%H:%M:%S")

            else:
                payload[field] = st.text_input(field.capitalize(), key=f"add_{endpoint}_{field}")

        if st.button("Add", key=f"add_btn_{endpoint}"):
            res = requests.post(f"{API_URL}/{endpoint}", json=payload)
            if res.ok:
                st.success("Added Successfully 🎉")
                st.balloons()
            else:
                st.error(res.text)

    # UPDATE
    with tabs[3]:
        item_id = st.number_input("ID to Update", min_value=1, key=f"update_id_{endpoint}")
        payload = {}

        for field in fields:
            if field in ["age", "patient_id", "doctor_id"]:
                payload[field] = st.number_input(f"New {field.capitalize()}", min_value=0, key=f"update_{endpoint}_{field}")

            elif field in ["gender", "status"]:
                options = ["Male", "Female", "Other"] if field == "gender" else ["Scheduled", "Completed", "Cancelled"]
                payload[field] = st.selectbox(f"New {field.capitalize()}", options, key=f"update_{endpoint}_{field}")

            elif field == "appointment_date":
                date_val = st.date_input("New Appointment Date")
                payload[field] = date_val.strftime("%Y-%m-%d")

            elif field == "appointment_time":
                time_val = st.time_input("New Appointment Time")
                payload[field] = time_val.strftime("%H:%M:%S")

            else:
                payload[field] = st.text_input(f"New {field.capitalize()}", key=f"update_{endpoint}_{field}")

        if st.button("Update", key=f"update_btn_{endpoint}"):
            res = requests.put(f"{API_URL}/{endpoint}/{item_id}", json=payload)
            if res.ok:
                st.success("Updated Successfully 🚀")
                st.balloons()
            else:
                st.error(res.text)

    # DELETE
    with tabs[4]:
        item_id = st.number_input("ID to Delete", min_value=1, key=f"delete_{endpoint}")
        if st.button("Delete", key=f"delete_btn_{endpoint}"):
            res = requests.delete(f"{API_URL}/{endpoint}/{item_id}")
            if res.ok:
                st.success("Deleted Successfully ❄")
                st.snow()
            else:
                st.error(res.text)

# =====================================================
# PATIENTS
# =====================================================
if menu == "Patients":
    crud_section(
        "👨‍⚕ Patients Management",
        "patients",
        ["name", "age", "gender", "phone", "address", "problem"]
    )

# =====================================================
# DOCTORS
# =====================================================
if menu == "Doctors":
    crud_section(
        "👩‍⚕ Doctors Management",
        "doctors",
        ["name", "specialization", "phone"]
    )

# =====================================================
# APPOINTMENTS
# =====================================================
if menu == "Appointments":
    crud_section(
        "📅 Appointments Management",
        "appointments",
        ["patient_id", "doctor_id", "appointment_date", "appointment_time", "status"]
    )