"""
Clean Database Script
AgriShield AI Platform
======================
Deletes all demo/test data from every operational table:
  - plant_diagnosis_records
  - prediction_history
  - irrigation_history
  - farmer_actions
  - follow_up_outcomes
  - model_version_records
  - plants (demo crops)
  - otps
  - revoked_tokens
  - test dummy users (testfarmer_dyn, tester_farmer)

Preserves real registered accounts (e.g. pandeeswaran776@gmail.com, veebika1803@gmail.com)
so sessions and logins remain intact with an empty, fresh slate.
"""
from sqlalchemy import text, inspect
from database.database import engine

def clean_database(keep_registered_users: bool = True):
    print("Connecting to database:", engine.url.render_as_string(hide_password=True))
    insp = inspect(engine)
    existing_tables = set(insp.get_table_names())
    print("Found tables:", existing_tables)

    # Tables to clear in safe foreign-key order
    data_tables = [
        "farmer_actions",
        "follow_up_outcomes",
        "plant_diagnosis_records",
        "prediction_history",
        "irrigation_history",
        "model_version_records",
        "plants",
        "otps",
        "revoked_tokens",
    ]

    with engine.begin() as conn:
        for t in data_tables:
            if t in existing_tables:
                count_before = conn.execute(text(f'SELECT COUNT(*) FROM "{t}"')).scalar()
                conn.execute(text(f'DELETE FROM "{t}"'))
                print(f"  Cleared {t} ({count_before} rows deleted)")

        if "users" in existing_tables:
            if keep_registered_users:
                # Remove known demo/test users
                demo_emails = [
                    "testfarmer_dyn@example.com",
                    "tester_farmer@agrishield.ai",
                ]
                for de in demo_emails:
                    conn.execute(text('DELETE FROM "users" WHERE email = :email'), {"email": de})
                remaining_users = conn.execute(text('SELECT id, name, email FROM "users"')).fetchall()
                print(f"  Retained registered users: {[u[2] for u in remaining_users]}")
            else:
                conn.execute(text('DELETE FROM "users"'))
                print("  Cleared all users")

    print("\n[OK] Database cleaned successfully! All demo records have been cleared.")

if __name__ == "__main__":
    clean_database(keep_registered_users=True)
