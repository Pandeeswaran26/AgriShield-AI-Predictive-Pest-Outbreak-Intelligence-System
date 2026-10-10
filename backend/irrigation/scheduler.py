"""
Irrigation Scheduler
AgriShield AI Platform
=======================
APScheduler-powered background job that automatically:
  - Sends morning irrigation alerts at 6:00 AM every day
  - Sends evening irrigation alerts at 6:00 PM every day

Uses the FastAPI lifespan pattern to start/stop cleanly with the server.
"""
import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from database.database import SessionLocal

logger = logging.getLogger("agrishield.irrigation.scheduler")


def _morning_dispatch_job():
    """Scheduled job: 6:00 AM daily — morning irrigation sweep."""
    logger.info(f"[IrrigationScheduler] 🌅 Morning dispatch triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    db = SessionLocal()
    try:
        # Import here to avoid circular imports at module level
        from irrigation.history_router import _run_scheduled_dispatch
        result = _run_scheduled_dispatch("morning_schedule", db, force_send=False)
        logger.info(
            f"[IrrigationScheduler] Morning dispatch complete — "
            f"{result['total_plants']} plants checked, "
            f"{result['total_alerts']} alerts sent."
        )
    except Exception as exc:
        logger.error(f"[IrrigationScheduler] Morning dispatch error: {exc}")
    finally:
        db.close()


def _evening_dispatch_job():
    """Scheduled job: 6:00 PM daily — evening irrigation sweep."""
    logger.info(f"[IrrigationScheduler] 🌇 Evening dispatch triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    db = SessionLocal()
    try:
        from irrigation.history_router import _run_scheduled_dispatch
        result = _run_scheduled_dispatch("evening_schedule", db, force_send=False)
        logger.info(
            f"[IrrigationScheduler] Evening dispatch complete — "
            f"{result['total_plants']} plants checked, "
            f"{result['total_alerts']} alerts sent."
        )
    except Exception as exc:
        logger.error(f"[IrrigationScheduler] Evening dispatch error: {exc}")
    finally:
        db.close()


def create_irrigation_scheduler() -> BackgroundScheduler:
    """
    Create and configure the irrigation background scheduler.
    Call .start() after creation and .shutdown() on app shutdown.
    """
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")  # IST — change as needed

    # Morning: 6:00 AM every day
    scheduler.add_job(
        _morning_dispatch_job,
        trigger=CronTrigger(hour=6, minute=0),
        id="morning_irrigation",
        name="Morning Irrigation Alert Dispatch",
        replace_existing=True,
        misfire_grace_time=300,  # 5-minute grace if server was briefly down
    )

    # Evening: 6:00 PM every day
    scheduler.add_job(
        _evening_dispatch_job,
        trigger=CronTrigger(hour=18, minute=0),
        id="evening_irrigation",
        name="Evening Irrigation Alert Dispatch",
        replace_existing=True,
        misfire_grace_time=300,
    )

    return scheduler
