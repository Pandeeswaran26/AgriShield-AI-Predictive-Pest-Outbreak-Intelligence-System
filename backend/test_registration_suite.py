import os
import sys
import json
import urllib.request
import urllib.error

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal
from auth.models import User, OTP

def make_request(url, method="GET", payload=None, token=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return err.code, parsed
    except Exception as exc:
        return 0, {"error": str(exc)}

def run_tests():
    print("=" * 65)
    print("AGRISHIELD AI — REGISTRATION & AUTHENTICATION TEST SUITE")
    print("=" * 65)

    backend_base = "http://127.0.0.1:8000"
    test_email = "automation_farmer@agrishield.ai"
    test_phone = "+91 9123456780"
    test_pwd = "FarmerSecret@2026"

    # Cleanup any previous test data for this test email
    db = SessionLocal()
    try:
        prev = db.query(User).filter(User.email == test_email).first()
        if prev:
            db.delete(prev)
            db.commit()
        db.query(OTP).filter(OTP.email == test_email).delete()
        db.commit()
    finally:
        db.close()

    results = []

    # -------------------------------------------------------------
    # 1. Register a new test user with valid details
    # -------------------------------------------------------------
    status, body = make_request(
        f"{backend_base}/auth/register",
        method="POST",
        payload={
            "name": "Automation Farmer",
            "email": test_email,
            "phone": test_phone,
            "location": "Thanjavur, Tamil Nadu",
            "password": test_pwd,
            "confirm_password": test_pwd,
        }
    )
    passed_1 = status == 200 and body.get("email") == test_email
    results.append(("1. Register new user with valid details", passed_1, f"Status: {status}, Response: {body.get('message')}"))
    print(f"[TEST 1] Register new user: {'PASS' if passed_1 else 'FAIL'} ({status})")

    # -------------------------------------------------------------
    # 2. Confirm successful database persistence
    # -------------------------------------------------------------
    db = SessionLocal()
    persisted_user = None
    latest_otp = None
    try:
        persisted_user = db.query(User).filter(User.email == test_email).first()
        otp_entry = db.query(OTP).filter(OTP.email == test_email, OTP.purpose == "register").order_by(OTP.created_at.desc()).first()
        if otp_entry:
            latest_otp = otp_entry.otp_code
    finally:
        db.close()

    passed_2 = persisted_user is not None and persisted_user.email == test_email and bool(latest_otp)
    results.append(("2. Confirm database persistence", passed_2, f"User ID: {persisted_user.id if persisted_user else None}, Has OTP: {bool(latest_otp)}"))
    print(f"[TEST 2] Database persistence confirmed: {'PASS' if passed_2 else 'FAIL'} (User ID: {persisted_user.id if persisted_user else None})")

    # -------------------------------------------------------------
    # 3. Verify OTP & Log in using newly registered user
    # -------------------------------------------------------------
    # Verify OTP first
    status_otp, body_otp = make_request(
        f"{backend_base}/auth/verify-otp",
        method="POST",
        payload={"email": test_email, "otp": latest_otp}
    )
    # Now log in
    status_login, body_login = make_request(
        f"{backend_base}/auth/login",
        method="POST",
        payload={"email": test_email, "password": test_pwd}
    )
    token = body_login.get("token")
    passed_3 = status_otp == 200 and status_login == 200 and bool(token)
    results.append(("3. Log in using newly registered user", passed_3, f"OTP Status: {status_otp}, Login Status: {status_login}, JWT received: {bool(token)}"))
    print(f"[TEST 3] Log in with new user: {'PASS' if passed_3 else 'FAIL'} ({status_login})")

    # -------------------------------------------------------------
    # 4. Attempt registration again with the same email (Duplicate check)
    # -------------------------------------------------------------
    status, body = make_request(
        f"{backend_base}/auth/register",
        method="POST",
        payload={
            "name": "Duplicate Farmer",
            "email": test_email,
            "phone": "9998887770",
            "location": "Salem",
            "password": "AnotherPassword@123",
            "confirm_password": "AnotherPassword@123",
        }
    )
    # Should return HTTP 409 Conflict with friendly message
    passed_4 = status == 409 and "already exists" in body.get("detail", "").lower()
    results.append(("4. Duplicate email returns HTTP 409", passed_4, f"Status: {status}, Detail: {body.get('detail')}"))
    print(f"[TEST 4] Duplicate email rejection (409): {'PASS' if passed_4 else 'FAIL'} ({status})")

    # -------------------------------------------------------------
    # 5. Submit mismatched passwords
    # -------------------------------------------------------------
    status, body = make_request(
        f"{backend_base}/auth/register",
        method="POST",
        payload={
            "name": "Mismatch Tester",
            "email": "mismatch@agrishield.ai",
            "phone": "9876500001",
            "location": "Erode",
            "password": "PasswordA@123",
            "confirm_password": "PasswordB@999",
        }
    )
    passed_5 = status == 400 and "passwords do not match" in body.get("detail", "").lower()
    results.append(("5. Password mismatch returns HTTP 400", passed_5, f"Status: {status}, Detail: {body.get('detail')}"))
    print(f"[TEST 5] Password mismatch rejection: {'PASS' if passed_5 else 'FAIL'} ({status})")

    # -------------------------------------------------------------
    # 6. Submit invalid email and phone values
    # -------------------------------------------------------------
    status, body = make_request(
        f"{backend_base}/auth/register",
        method="POST",
        payload={
            "name": "Invalid Input Farmer",
            "email": "not-an-email",
            "phone": "123", # Too short (<10 digits)
            "location": "Madurai",
            "password": "ValidPassword@123",
            "confirm_password": "ValidPassword@123",
        }
    )
    passed_6 = status == 422
    results.append(("6. Invalid email & phone return HTTP 422", passed_6, f"Status: {status}, Validation count: {len(body.get('detail', []))}"))
    print(f"[TEST 6] Invalid email/phone rejection (422): {'PASS' if passed_6 else 'FAIL'} ({status})")

    # -------------------------------------------------------------
    # 7. Test missing required fields
    # -------------------------------------------------------------
    status, body = make_request(
        f"{backend_base}/auth/register",
        method="POST",
        payload={
            "name": "", # min_length violation
            # Missing email, phone, location
            "password": "ValidPassword@123",
            "confirm_password": "ValidPassword@123",
        }
    )
    passed_7 = status == 422
    results.append(("7. Missing required fields return HTTP 422", passed_7, f"Status: {status}"))
    print(f"[TEST 7] Missing required fields rejection: {'PASS' if passed_7 else 'FAIL'} ({status})")

    # -------------------------------------------------------------
    # 8. Test backend-unavailable handling
    # -------------------------------------------------------------
    status, body = make_request(
        "http://127.0.0.1:8999/auth/register",
        method="POST",
        payload={"email": "any@farm.com"}
    )
    passed_8 = status == 0 and "error" in body
    results.append(("8. Backend unavailable handled (Status 0)", passed_8, f"Error: {body.get('error')}"))
    print(f"[TEST 8] Backend unavailable handled: {'PASS' if passed_8 else 'FAIL'} (Connection refused caught)")

    # -------------------------------------------------------------
    # 9. Verify that failed registrations do not leave partial records
    # -------------------------------------------------------------
    db = SessionLocal()
    ghost_user = None
    try:
        ghost_user = db.query(User).filter(User.email == "mismatch@agrishield.ai").first()
    finally:
        db.close()
    passed_9 = ghost_user is None
    results.append(("9. Failed registrations leave zero phantom records", passed_9, f"Ghost user found: {ghost_user is not None}"))
    print(f"[TEST 9] Zero partial records on failed registration: {'PASS' if passed_9 else 'FAIL'}")

    # Final Cleanup of test account
    db = SessionLocal()
    try:
        test_u = db.query(User).filter(User.email == test_email).first()
        if test_u:
            db.delete(test_u)
            db.commit()
        db.query(OTP).filter(OTP.email == test_email).delete()
        db.commit()
    finally:
        db.close()

    print("\n" + "=" * 65)
    print("REGISTRATION TEST SUMMARY")
    print("=" * 65)
    all_ok = True
    for name, p, det in results:
        status_str = "PASS [OK]" if p else "FAIL [X]"
        print(f"{status_str} | {name} -> {det}")
        if not p:
            all_ok = False

    print("=" * 65)
    print(f"OVERALL STATUS: {'ALL 9 TESTS PASSED' if all_ok else 'SOME TESTS FAILED'}")
    print("=" * 65)
    return all_ok

if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
