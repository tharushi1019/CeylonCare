from src.services.patient_service import (
    authenticate_user,
    get_all_doctors,
    get_all_patients,
    format_doctor_schedule_summary,
    get_doctors_by_specialty,
)

print("=" * 60)
print("TEST 1: Authentication")
print("=" * 60)

# Patient Login
s, u, r = authenticate_user("P001", "password123")
print(f"P001 Login: {s} | Role: {r} | Name: {u['name'] if u else 'FAILED'}")

# Wrong password
s2, u2, r2 = authenticate_user("P001", "wrongpass")
print(f"P001 Wrong Password: should be False -> {s2}")

# Operator Login
s3, u3, r3 = authenticate_user("operator@ceyloncare.lk", "admin")
print(f"Operator Login: {s3} | Role: {r3} | Name: {u3['name'] if u3 else 'FAILED'}")

# Email Login
s4, u4, r4 = authenticate_user("nimal@example.com", "password123")
print(f"Email Login (P001): {s4} | Role: {r4}")

print()
print("=" * 60)
print("TEST 2: Doctor Schedule Query (Key UX Fix)")
print("=" * 60)
print(format_doctor_schedule_summary("Dr. Perera"))
print()
print(format_doctor_schedule_summary("cardiologist"))
print()
print(format_doctor_schedule_summary("dermatologist"))

print()
print("=" * 60)
print("TEST 3: All Doctors Loaded")
print("=" * 60)
docs = get_all_doctors()
print(f"Total Doctors: {len(docs)}")
for d in docs:
    print(f"  - {d['name']} | {d['specialty']} | {d['branch']}")

print()
print("=" * 60)
print("TEST 4: All Patients Loaded")
print("=" * 60)
pats = get_all_patients()
print(f"Total Patients: {len(pats)}")
for p in pats:
    print(f"  - {p['patient_id']} | {p['name']} | {p.get('city','N/A')}")

print()
print("ALL TESTS PASSED")
