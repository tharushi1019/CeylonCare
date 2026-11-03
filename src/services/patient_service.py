import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Tuple


# ============================================================
# CeylonCare Patient Management & EHR Service
# ============================================================
# Production-ready data-service layer for CeylonCare Health Network.
# Integrates with CeylonCare multi-branch EHR (Colombo, Kandy, Galle),
# doctor directory, patient authentication, appointments, and patient feedback.
# ============================================================


DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "ceyloncare"
PATIENTS_FILE = DATA_DIR / "patients.json"
DOCTORS_FILE = DATA_DIR / "doctors_directory.json"
FEEDBACK_FILE = DATA_DIR / "patient_feedback.json"


def _ensure_data_file():
    """
    Create the CeylonCare data directory and JSON files
    if they do not already exist.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not PATIENTS_FILE.exists():
        initial_data = {
            "users": [
                {
                    "user_id": "OP001",
                    "email": "operator@ceyloncare.lk",
                    "password": "admin",
                    "role": "operator",
                    "name": "Sister Kamala Wijesinghe (Chief Triage Operator)",
                    "branch": "Colombo Central Hospital"
                }
            ],
            "patients": [],
            "appointments": [],
            "visit_history": []
        }
        PATIENTS_FILE.write_text(
            json.dumps(initial_data, indent=4),
            encoding="utf-8"
        )


def _load_data() -> dict:
    """Load CeylonCare patient-management and EHR data."""
    _ensure_data_file()
    try:
        return json.loads(PATIENTS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {
            "users": [],
            "patients": [],
            "appointments": [],
            "visit_history": []
        }


def _save_data(data: dict):
    """Save CeylonCare patient-management and EHR data."""
    _ensure_data_file()
    PATIENTS_FILE.write_text(
        json.dumps(data, indent=4),
        encoding="utf-8"
    )


def _load_doctors_data() -> dict:
    """Load doctors and branches directory."""
    if DOCTORS_FILE.exists():
        try:
            return json.loads(DOCTORS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"branches": [], "doctors": []}


# ============================================================
# Doctor & Hospital Directory Lookups
# ============================================================

def get_all_doctors() -> List[dict]:
    """Retrieve all consultant doctors across CeylonCare branches."""
    return _load_doctors_data().get("doctors", [])


def get_all_branches() -> List[dict]:
    """Retrieve all hospital branches."""
    return _load_doctors_data().get("branches", [])


def get_doctors_by_specialty(specialist_or_dept: str) -> List[dict]:
    """
    Find doctors matching a specialist role or department.
    e.g. 'cardiology', 'cardiologist', 'dermatologist', 'general physician'
    """
    query = specialist_or_dept.strip().lower()
    results = []
    for doc in get_all_doctors():
        spec = doc.get("specialty", "").lower()
        dept = doc.get("department", "").lower()
        if query in spec or query in dept or spec in query or dept in query:
            results.append(doc)
    return results


def get_doctor_schedule(query: str) -> Optional[dict]:
    """
    Look up schedule for a doctor name or specialty.
    Examples: 'Dr. Perera', 'Perera', 'cardiologist', 'Dr. K. Perera'
    """
    q = query.strip().lower()
    docs = get_all_doctors()

    # 1. Exact substring match (handles full name queries)
    for doc in docs:
        if q in doc.get("name", "").lower():
            return doc

    # 2. Word-level token match (handles last-name-only queries like 'Perera')
    q_words = [w.rstrip(".").strip() for w in q.split() if len(w) > 2 and w not in ("dr", "the", "with", "see")]
    for doc in docs:
        doc_name_tokens = [t.lower().rstrip(".") for t in doc.get("name", "").split()]
        if any(word in doc_name_tokens for word in q_words):
            return doc

    # 3. Match by specialty / department
    by_spec = get_doctors_by_specialty(query)
    if by_spec:
        return by_spec[0]

    return None


def format_doctor_directory_summary(doctor_or_specialty: str) -> str:
    """Format doctor information into a clear conversational response."""
    q = doctor_or_specialty.strip()
    doc = get_doctor_schedule(q)
    
    if doc:
        return (
            f"**{doc['name']}** ({doc['specialty']} - {doc['department']})\n"
            f"Branch: {doc['branch']} ({doc.get('room', 'Consultation Room')})\n"
            f"Schedule: {doc['schedule']}\n"
            f"Consultation Fee: LKR {doc['consultation_fee']:,}\n\n"
            f"Would you like to book an appointment with {doc['name']}? "
            f"Just let me know your preferred date and time!"
        )
        
    matching = get_doctors_by_specialty(q)
    if matching:
        lines = [f"Here are the available specialists for **{q.title()}**:"]
        for d in matching:
            lines.append(
                f"- **{d['name']}** ({d['branch']}): {d['schedule']} | Fee: LKR {d['consultation_fee']:,}"
            )
        lines.append("\nPlease let me know which doctor and date you would like to book.")
        return "\n".join(lines)
        
    return (
        f"I could not find a specific schedule for '{doctor_or_specialty}'. "
        "Our main specialties include Cardiology (Dr. K. Perera, Dr. S. Fernando), "
        "General Medicine (Dr. N. Jayasinghe, Dr. A. Silva), Pediatrics (Dr. M. De Silva), "
        "Neurology (Dr. R. Wickramasinghe), and Dermatology (Dr. T. Abeywardena)."
    )


# ============================================================
# User Authentication & Registration (Login / Signup)
# ============================================================

def authenticate_user(identifier: str, password: str) -> Tuple[bool, Optional[dict], str]:
    """
    Authenticate a user by Patient ID or Email.
    Returns: (is_success, user_or_patient_dict, role)
    Roles: 'operator' or 'patient'
    """
    ident = identifier.strip().lower()
    pwd = password.strip()
    data = _load_data()

    # 1. Check Clinical Operators / Staff
    for user in data.get("users", []):
        if user["email"].lower() == ident and user["password"] == pwd:
            return True, user, "operator"

    # 2. Check Patients
    for pat in data.get("patients", []):
        pat_id = pat.get("patient_id", "").lower()
        pat_email = pat.get("email", "").lower()
        if (pat_id == ident or pat_email == ident) and pat.get("password") == pwd:
            return True, pat, "patient"

    return False, None, ""


def register_patient(
    name: str,
    email: str,
    password: str,
    date_of_birth: str,
    phone: str,
    city: str = "Colombo",
    gender: str = "Not Specified",
    blood_group: str = "O+",
    chronic_conditions: Optional[List[str]] = None,
    emergency_contact: str = ""
) -> Tuple[bool, str, Optional[dict]]:
    """
    Register a new patient into the CeylonCare EHR.
    Returns: (is_success, message_or_error, patient_record)
    """
    data = _load_data()
    email_clean = email.strip().lower()

    # Check for duplicate email
    for p in data.get("patients", []):
        if p.get("email", "").lower() == email_clean:
            return False, f"A patient account with email '{email}' already exists.", None

    # Generate sequential patient ID: P011, P012...
    existing_ids = [
        int(p["patient_id"][1:])
        for p in data.get("patients", [])
        if p.get("patient_id", "").startswith("P") and p["patient_id"][1:].isdigit()
    ]
    next_num = max(existing_ids) + 1 if existing_ids else 1
    new_patient_id = f"P{next_num:03d}"

    new_patient = {
        "patient_id": new_patient_id,
        "name": name.strip(),
        "email": email_clean,
        "password": password.strip(),
        "date_of_birth": date_of_birth.strip(),
        "phone": phone.strip(),
        "gender": gender,
        "city": city,
        "blood_group": blood_group,
        "chronic_conditions": chronic_conditions or [],
        "emergency_contact": emergency_contact.strip()
    }

    data.setdefault("patients", []).append(new_patient)
    _save_data(data)
    return True, f"Patient account created successfully! Your Patient ID is {new_patient_id}.", new_patient


# ============================================================
# Patient Retrieval Operations
# ============================================================

def get_patient(patient_id: str) -> Optional[dict]:
    """Retrieve a patient record by ID."""
    data = _load_data()
    for patient in data.get("patients", []):
        if patient.get("patient_id", "").lower() == patient_id.strip().lower():
            return patient
    return None


def get_all_patients() -> List[dict]:
    """Retrieve all registered patients in CeylonCare EHR."""
    return _load_data().get("patients", [])


def create_patient(patient_id: str, name: str) -> dict:
    """Create a patient record (backward compatibility)."""
    data = _load_data()
    patient = {
        "patient_id": patient_id.strip(),
        "name": name.strip(),
        "email": f"{patient_id.lower()}@ceyloncare.lk",
        "password": "password123",
        "city": "Colombo",
        "blood_group": "B+",
        "chronic_conditions": [],
        "emergency_contact": ""
    }
    data.setdefault("patients", []).append(patient)
    _save_data(data)
    return patient


# ============================================================
# Appointment Operations & Slot Validation
# ============================================================

def create_appointment(
    patient_id: str,
    specialist: str,
    appointment_date: str,
    appointment_time: str,
    doctor: str = "",
    branch: str = ""
) -> dict:
    """
    Create an appointment linked to a patient.
    Includes conflict detection to prevent double-booking identical doctor-time slots.
    """
    data = _load_data()

    # Determine doctor and branch if not specified
    if not doctor or not branch:
        doc_info = get_doctor_schedule(specialist)
        if doc_info:
            doctor = doctor or doc_info.get("name", "")
            branch = branch or doc_info.get("branch", "Colombo Central Hospital")
        else:
            branch = branch or "Colombo Central Hospital"

    # Slot Conflict Validation: Check if doctor already has a confirmed booking at this exact slot
    for app in data.get("appointments", []):
        if (
            app.get("status", "").lower() == "confirmed"
            and app.get("doctor", "").lower() == doctor.strip().lower()
            and app.get("date", "").strip() == appointment_date.strip()
            and app.get("time", "").strip().lower() == appointment_time.strip().lower()
        ):
            # Slot collision detected
            return {
                "appointment_id": None,
                "status": "conflict",
                "error": f"Time slot {appointment_time} on {appointment_date} with {doctor} is already booked. Please choose an alternate slot.",
                "doctor": doctor,
                "branch": branch,
                "date": appointment_date,
                "time": appointment_time
            }

    appointment_id = f"APT-{len(data.get('appointments', [])) + 1001:04d}"

    appointment = {
        "appointment_id": appointment_id,
        "patient_id": patient_id,
        "doctor": doctor,
        "specialist": specialist,
        "branch": branch,
        "date": appointment_date,
        "time": appointment_time,
        "status": "confirmed"
    }

    data.setdefault("appointments", []).append(appointment)
    _save_data(data)
    return appointment


def get_patient_appointments(patient_id: str) -> list:
    """Retrieve all appointments belonging to a patient."""
    data = _load_data()
    return [
        app for app in data.get("appointments", [])
        if app.get("patient_id", "").lower() == patient_id.strip().lower()
    ]


def get_all_appointments() -> list:
    """Retrieve all appointments across all hospital branches."""
    return _load_data().get("appointments", [])


def find_appointment(
    patient_id: str,
    specialist: str,
    appointment_date: str,
    appointment_time: str
) -> Optional[dict]:
    """Find an existing appointment matching the patient and details."""
    data = _load_data()
    for appointment in data.get("appointments", []):
        if (
            appointment.get("patient_id", "").lower() == patient_id.strip().lower()
            and (
                appointment.get("specialist", "").lower() == specialist.strip().lower()
                or specialist.strip().lower() in appointment.get("doctor", "").lower()
            )
            and appointment.get("date", "").lower() == appointment_date.strip().lower()
            and appointment.get("time", "").lower() == appointment_time.strip().lower()
            and appointment.get("status", "").lower() == "confirmed"
        ):
            return appointment
    return None


def cancel_appointment(patient_id: str, appointment_id: str) -> Optional[dict]:
    """Cancel an existing appointment for a patient."""
    data = _load_data()
    for appointment in data.get("appointments", []):
        if (
            appointment.get("patient_id", "").lower() == patient_id.strip().lower()
            and appointment.get("appointment_id", "").lower() == appointment_id.strip().lower()
        ):
            if appointment.get("status", "").lower() == "cancelled":
                return appointment
            appointment["status"] = "cancelled"
            _save_data(data)
            return appointment
    return None


def reschedule_appointment(
    patient_id: str,
    appointment_id: str,
    new_date: str,
    new_time: str
) -> Optional[dict]:
    """Reschedule an existing confirmed appointment."""
    data = _load_data()
    target = None

    for app in data.get("appointments", []):
        if (
            app.get("appointment_id", "").lower() == appointment_id.strip().lower()
            and app.get("patient_id", "").lower() == patient_id.strip().lower()
        ):
            target = app
            break

    if not target or target.get("status", "").lower() != "confirmed":
        return None

    target["date"] = new_date
    target["time"] = new_time
    _save_data(data)
    return target


# ============================================================
# Longitudinal EHR Visit History & Summarization
# ============================================================

def add_visit_record(
    patient_id: str,
    visit_date: str,
    department: str,
    reason: str,
    summary: str,
    outcome: str,
    doctor: str = "",
    branch: str = "Colombo Central Hospital",
    icd11_code: str = ""
) -> dict:
    """Add a patient clinical visit record."""
    data = _load_data()
    visit_id = f"VIS-{len(data.get('visit_history', [])) + 1:03d}"

    visit = {
        "visit_id": visit_id,
        "patient_id": patient_id,
        "date": visit_date,
        "department": department,
        "doctor": doctor,
        "branch": branch,
        "icd11_code": icd11_code,
        "reason": reason,
        "summary": summary,
        "outcome": outcome
    }

    data.setdefault("visit_history", []).append(visit)
    _save_data(data)
    return visit


def get_visit_history(patient_id: str) -> list:
    """Retrieve visit history for a patient."""
    data = _load_data()
    return [
        v for v in data.get("visit_history", [])
        if v.get("patient_id", "").lower() == patient_id.strip().lower()
    ]


def format_visit_history(patient_id: str) -> str:
    """Return a formatted human-readable summary of a patient's visit history."""
    patient = get_patient(patient_id)
    if not patient:
        return f"No patient record was found for patient ID {patient_id}."

    visits = get_visit_history(patient_id)
    if not visits:
        return f"No prior visit history recorded for patient {patient['name']} ({patient_id})."

    lines = [
        f"### Patient EHR Clinical Profile: {patient['name']} ({patient['patient_id']})",
        f"• **Demographics:** {patient.get('gender', 'N/A')} | DOB: {patient.get('date_of_birth', 'N/A')} | Blood Group: `{patient.get('blood_group', 'N/A')}`",
        f"• **Primary Branch:** {patient.get('city', 'Colombo')} Branch",
        f"• **Documented Conditions:** {', '.join(patient.get('chronic_conditions', [])) or 'None recorded'}",
        f"• **Emergency Contact:** {patient.get('emergency_contact', 'N/A')}",
        "",
        "#### Longitudinal Clinical Encounters & Records:"
    ]

    for v in visits:
        lines.append(f"\n---")
        lines.append(f"🏥 **Visit ID {v['visit_id']} ({v['date']})** — {v.get('branch', 'Hospital')}")
        lines.append(f"• **Department:** {v['department']} | **Consultant:** {v.get('doctor', 'Attending Physician')}")
        if v.get("icd11_code"):
            lines.append(f"• **ICD-11 Code / Diagnosis:** `{v['icd11_code']}`")
        lines.append(f"• **Presenting Reason:** {v['reason']}")
        if v.get("vitals"):
            vitals = v["vitals"]
            lines.append(f"• **Recorded Vitals:** BP: `{vitals.get('blood_pressure')}` | HR: `{vitals.get('heart_rate')}` | SpO2: `{vitals.get('spo2')}` | BMI: `{vitals.get('bmi')}`")
        if v.get("investigations"):
            lines.append(f"• **Diagnostic Investigations:** {v['investigations']}")
        lines.append(f"• **Clinical Findings:** {v['summary']}")
        lines.append(f"• **Outcome & Action Plan:** {v['outcome']}")

    return "\n".join(lines)


# ============================================================
# Patient Feedback & Continuous Quality Improvement
# ============================================================

def submit_patient_feedback(
    patient_id: str,
    rating: int,
    comment: str,
    service_category: str = "General Patient Service"
) -> dict:
    """
    Submit patient satisfaction feedback for continuous agentic performance tracking.
    Persists feedback to patient_feedback.json.
    """
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    feedback_list = []
    if FEEDBACK_FILE.exists():
        try:
            feedback_list = json.loads(FEEDBACK_FILE.read_text(encoding="utf-8"))
        except Exception:
            feedback_list = []

    feedback_id = f"FBK-{len(feedback_list) + 1:04d}"
    record = {
        "feedback_id": feedback_id,
        "patient_id": patient_id,
        "rating": int(rating),
        "comment": comment.strip(),
        "service_category": service_category,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    feedback_list.append(record)
    FEEDBACK_FILE.write_text(json.dumps(feedback_list, indent=4), encoding="utf-8")
    return record


def get_all_feedback() -> List[dict]:
    """Retrieve all submitted patient service feedback."""
    if FEEDBACK_FILE.exists():
        try:
            return json.loads(FEEDBACK_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def get_feedback_summary() -> dict:
    """Calculate average customer satisfaction (CSAT) rating and feedback count."""
    items = get_all_feedback()
    if not items:
        return {"count": 0, "average_rating": 5.0, "csat_percentage": 100.0}
    ratings = [f.get("rating", 5) for f in items]
    avg = sum(ratings) / len(ratings)
    positive = len([r for r in ratings if r >= 4])
    return {
        "count": len(items),
        "average_rating": round(avg, 2),
        "csat_percentage": round((positive / len(items)) * 100, 1)
    }
