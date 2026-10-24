import sys
import os
import json
import urllib.request
import urllib.error

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal
from auth.models import User, OTP
from auth.service import hash_password, verify_password

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

def run_all_auth_tests():
    print("=" * 60)
    print("AGRISHIELD AI — COMPLETE AUTHENTICATION VERIFICATION SUITE")
    print("=" * 60)

    backend_base = "http://127.0.0.1:8000"
    vite_base = "http://localhost:5173"

    results = []

    # 1. Health checks
    status, body = make_request(f"{backend_base}/health")
    passed = status == 200 and body.get("status") == "Healthy"
    results.append(("Backend /health availability", passed, f"Status: {status}, Body: {body}"))
    print(f"[TEST 1] Backend health: {'PASS' if passed else 'FAIL'} ({status})")

    # 2. Vite proxy /auth/login routing check
    status, body = make_request(f"{vite_base}/auth/login", method="POST", payload={"email": "invalid_format", "password": "123"})
    # Expect 422 Unprocessable Entity because email is not valid email format
    passed = status == 422
    results.append(("Vite proxy /auth/login routing", passed, f"Status: {status}, Response: {body}"))
    print(f"[TEST 2] Vite proxy /auth/login reachable: {'PASS' if passed else 'FAIL'} ({status})")

    # 3. Test valid credentials with existing user
    status, body = make_request(
        f"{backend_base}/auth/login",
        method="POST",
        payload={"email": "tester_farmer@agrishield.ai", "password": "AgriShield@2026"}
    )
    token = body.get("token")
    passed = status == 200 and bool(token) and body.get("email") == "tester_farmer@agrishield.ai"
    results.append(("Valid credentials login", passed, f"Status: {status}, User: {body.get('name')}, Has token: {bool(token)}"))
    print(f"[TEST 3] Valid credentials login: {'PASS' if passed else 'FAIL'} ({status})")

    # 4. Test case-insensitivity on email during login
    status, body = make_request(
        f"{backend_base}/auth/login",
        method="POST",
        payload={"email": "TESTER_FARMER@agrishield.ai", "password": "AgriShield@2026"}
    )
    passed = status == 200 and bool(body.get("token"))
    results.append(("Case-insensitive email login", passed, f"Status: {status}, Has token: {bool(body.get('token'))}"))
    print(f"[TEST 4] Case-insensitive email login: {'PASS' if passed else 'FAIL'} ({status})")

    # 5. Test invalid password
    status, body = make_request(
        f"{backend_base}/auth/login",
        method="POST",
        payload={"email": "tester_farmer@agrishield.ai", "password": "WrongPassword999!"}
    )
    passed = status == 401 and body.get("detail") == "Invalid email or password."
    results.append(("Invalid password returns 401", passed, f"Status: {status}, Detail: {body.get('detail')}"))
    print(f"[TEST 5] Invalid password 401 check: {'PASS' if passed else 'FAIL'} ({status})")

    # 6. Test nonexistent email
    status, body = make_request(
        f"{backend_base}/auth/login",
        method="POST",
        payload={"email": "nonexistent_farmer_9999@agrishield.ai", "password": "AnyPassword123!"}
    )
    passed = status == 401 and "Please register first" in body.get("detail", "")
    results.append(("Nonexistent email returns registration guidance", passed, f"Status: {status}, Detail: {body.get('detail')}"))
    print(f"[TEST 6] Nonexistent email registration prompt: {'PASS' if passed else 'FAIL'} ({status})")

    # 7. Test malformed payload (422 validation error)
    status, body = make_request(
        f"{backend_base}/auth/login",
        method="POST",
        payload={"email": "not-an-email", "password": "123"}
    )
    passed = status == 422 and "detail" in body
    results.append(("Malformed input returns 422", passed, f"Status: {status}, Detail: {body.get('detail')}"))
    print(f"[TEST 7] Malformed email validation 422: {'PASS' if passed else 'FAIL'} ({status})")

    # 8. Test JWT handling and protected route /auth/me
    status, body = make_request(
        f"{backend_base}/auth/me",
        method="GET",
        token=token
    )
    passed = status == 200 and body.get("email") == "tester_farmer@agrishield.ai"
    results.append(("Protected route /auth/me with JWT", passed, f"Status: {status}, User: {body.get('name')}"))
    print(f"[TEST 8] Protected route /auth/me: {'PASS' if passed else 'FAIL'} ({status})")

    # 9. Test protected route with invalid/missing token
    status, body = make_request(
        f"{backend_base}/auth/me",
        method="GET",
        token="invalid.bearer.token"
    )
    passed = status == 401
    results.append(("Protected route without valid token rejected", passed, f"Status: {status}, Detail: {body.get('detail')}"))
    print(f"[TEST 9] Protected route rejection: {'PASS' if passed else 'FAIL'} ({status})")

    # 10. Test registration followed by OTP verification and login
    test_new_email = "new_flow_farmer@agrishield.ai"
    test_new_phone = "9845012349"
    test_new_pwd = "NewSecurePassword@2026"

    # Cleanup if previously exists
    db = SessionLocal()
    try:
        old_user = db.query(User).filter(User.email == test_new_email).first()
        if old_user:
            db.delete(old_user)
            db.commit()
    finally:
        db.close()

    # Step A: Register
    status, body = make_request(
        f"{backend_base}/auth/register",
        method="POST",
        payload={
            "name": "New Farmer",
            "email": test_new_email,
            "phone": test_new_phone,
            "location": "Madurai, Tamil Nadu",
            "password": test_new_pwd,
            "confirm_password": test_new_pwd
        }
    )
    reg_ok = status == 200
    print(f"[TEST 10A] Register new user: {'PASS' if reg_ok else 'FAIL'} ({status})")

    # Step B: Attempt login before OTP verification (Should be 403 unverified)
    status, body = make_request(
        f"{backend_base}/auth/login",
        method="POST",
        payload={"email": test_new_email, "password": test_new_pwd}
    )
    unverified_blocked = status == 403 and "not verified" in body.get("detail", "").lower()
    print(f"[TEST 10B] Block unverified user: {'PASS' if unverified_blocked else 'FAIL'} ({status})")

    # Step C: Retrieve OTP from DB and verify
    db = SessionLocal()
    otp_code = None
    try:
        otp_entry = db.query(OTP).filter(OTP.email == test_new_email, OTP.purpose == "register").order_by(OTP.created_at.desc()).first()
        if otp_entry:
            otp_code = otp_entry.otp_code
    finally:
        db.close()

    if otp_code:
        status, body = make_request(
            f"{backend_base}/auth/verify-otp",
            method="POST",
            payload={"email": test_new_email, "otp": otp_code}
        )
        verify_ok = status == 200 and bool(body.get("token"))
        print(f"[TEST 10C] Verify OTP: {'PASS' if verify_ok else 'FAIL'} ({status})")

        # Step D: Login after verification
        status, body = make_request(
            f"{backend_base}/auth/login",
            method="POST",
            payload={"email": test_new_email, "password": test_new_pwd}
        )
        post_reg_login_ok = status == 200 and bool(body.get("token"))
        print(f"[TEST 10D] Login after OTP verification: {'PASS' if post_reg_login_ok else 'FAIL'} ({status})")

        passed_10 = reg_ok and unverified_blocked and verify_ok and post_reg_login_ok
    else:
        passed_10 = False

    results.append(("Full registration -> OTP verification -> login flow", passed_10, "Complete lifecycle"))

    # Cleanup created user
    db = SessionLocal()
    try:
        user_to_clean = db.query(User).filter(User.email == test_new_email).first()
        if user_to_clean:
            db.delete(user_to_clean)
            db.commit()
    finally:
        db.close()

    # 11. Test Backend Unavailable handling simulation
    # Port 8999 is guaranteed closed / not listening
    status, body = make_request(
        "http://127.0.0.1:8999/auth/login",
        method="POST",
        payload={"email": "test@agrishield.ai", "password": "password"}
    )
    passed = status == 0 and "error" in body
    results.append(("Backend unavailable returns connection error (status 0)", passed, f"Error: {body.get('error')}"))
    print(f"[TEST 11] Backend unavailable simulation: {'PASS' if passed else 'FAIL'} (Caught error correctly)")

    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    all_passed = True
    for title, passed, detail in results:
        status_str = "PASS [OK]" if passed else "FAIL [X]"
        print(f"{status_str} | {title} -> {detail}")
        if not passed:
            all_passed = False

    print("=" * 60)
    print(f"OVERALL STATUS: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("=" * 60)
    return all_passed

if __name__ == "__main__":
    success = run_all_auth_tests()
    sys.exit(0 if success else 1)
