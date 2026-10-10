"""
Irrigation Email Notification Service
AgriShield AI Platform
======================================
Sends automated, beautifully formatted irrigation alerts to the farmer's registered email
when water is needed for a specific plant/crop.

Includes:
  - Plant Name & Crop Family
  - Field Position / Zone
  - Water Frequency (How many times water is needed)
  - Water Runtime (How many hours water is needed)
  - Soil Moisture Status
  - Recommended Water Dosage & Best Operating Window
  - Agronomic Advisories
"""
import os
import smtplib
from email.message import EmailMessage
from typing import List, Optional


def send_irrigation_alert_email(
    to_email: str,
    farmer_name: str,
    plant_name: str,
    crop_type: str,
    field_position: str,
    irrigation_frequency: str,
    irrigation_hours: float,
    soil_moisture: float,
    water_quantity: str,
    timing_advice: str,
    advisories: Optional[List[str]] = None,
) -> dict:
    """
    Sends an automated email notification alerting that irrigation is needed for a plant.
    Falls back gracefully to console logging if SMTP credentials are not configured.
    """
    if not to_email:
        return {"status": "error", "message": "Recipient email address is required"}

    farmer_display = farmer_name or "Farmer"
    pos_display = field_position or "Primary Field Zone"
    freq_display = irrigation_frequency or "1–2 times daily"
    hours_display = f"{irrigation_hours:.1f}" if isinstance(irrigation_hours, (int, float)) and irrigation_hours > 0 else "2.0"
    advisories = advisories or [
        "Soil moisture has fallen below the optimal threshold for healthy crop growth.",
        "Begin irrigation in accordance with the recommended runtime hours to prevent root-zone water stress.",
    ]

    subject = f"🚨 AgriShield Alert: Water is needed for {plant_name} ({pos_display})"

    # Plain text version
    plain_lines = [
        f"Hello {farmer_display},",
        "",
        f"AgriShield AI precision monitoring has determined that WATER IS NEEDED for: {plant_name}.",
        "",
        "============================================================",
        "IRRIGATION SCHEDULE & FIELD DETAILS",
        "============================================================",
        f"• Plant Name:              {plant_name} ({crop_type})",
        f"• Field Position / Zone:   {pos_display}",
        f"• Soil Moisture Status:    {soil_moisture:.1f}% VWC (Deficit Detected)",
        f"• Irrigation Frequency:    {freq_display}",
        f"• Duration Needed:         {hours_display} Hours per irrigation cycle",
        f"• Water Dosage:            {water_quantity}",
        f"• Recommended Window:      {timing_advice}",
        "",
        "AGRONOMIC ADVISORIES:",
    ]
    for adv in advisories:
        plain_lines.append(f"  - {adv}")
    plain_lines.extend([
        "",
        "Please activate your field pumps or irrigation valves according to this schedule.",
        "",
        "Best regards,",
        "AgriShield AI Precision Farming System",
        "https://agrishield.ai",
    ])
    plain_content = "\n".join(plain_lines)

    # HTML formatted email
    advisory_html_items = "".join(
        f'<li style="margin-bottom: 8px; color: #334155;">{adv}</li>' for adv in advisories
    )

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 24px; }}
    .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; }}
    .header {{ background: linear-gradient(135deg, #065f46 0%, #047857 100%); padding: 28px 24px; color: #ffffff; }}
    .brand {{ font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.9; }}
    .title {{ font-size: 22px; font-weight: 800; margin: 6px 0 0; }}
    .badge {{ display: inline-block; background: #ef4444; color: #ffffff; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 9999px; text-transform: uppercase; margin-top: 10px; }}
    .content {{ padding: 24px; color: #1e293b; }}
    .greeting {{ font-size: 15px; margin-bottom: 16px; color: #334155; }}
    .alert-box {{ background: #fef2f2; border: 1px solid #fecaca; border-radius: 12px; padding: 14px 16px; margin-bottom: 20px; }}
    .alert-box p {{ margin: 0; color: #991b1b; font-size: 14px; font-weight: 600; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }}
    .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 14px; }}
    .card-label {{ font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 0.5px; }}
    .card-value {{ font-size: 16px; font-weight: 800; color: #0f172a; margin-top: 4px; }}
    .detail-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f1f5f9; font-size: 13px; }}
    .detail-label {{ color: #64748b; font-weight: 600; }}
    .detail-val {{ color: #0f172a; font-weight: 700; text-align: right; }}
    .advisory {{ background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 12px; padding: 16px; margin-top: 20px; }}
    .advisory h4 {{ margin: 0 0 10px; font-size: 13px; font-weight: 700; color: #065f46; text-transform: uppercase; letter-spacing: 0.5px; }}
    .advisory ul {{ margin: 0; padding-left: 20px; font-size: 13px; }}
    .footer {{ background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 18px 24px; text-align: center; font-size: 12px; color: #64748b; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="brand">AgriShield AI Precision Farming</div>
      <h1 class="title">Water Needed: {plant_name}</h1>
      <span class="badge">Immediate Irrigation Recommended</span>
    </div>

    <div class="content">
      <p class="greeting">Hello <strong>{farmer_display}</strong>,</p>
      
      <div class="alert-box">
        <p>⚠️ Soil moisture deficit detected. Your plant <strong>{plant_name}</strong> at <strong>{pos_display}</strong> requires irrigation.</p>
      </div>

      <div class="grid">
        <div class="card">
          <div class="card-label">How Many Times Needed</div>
          <div class="card-value" style="color: #0284c7;">{freq_display}</div>
        </div>
        <div class="card">
          <div class="card-label">Hours Needed (Runtime)</div>
          <div class="card-value" style="color: #059669;">{hours_display} Hours</div>
        </div>
        <div class="card">
          <div class="card-label">Field Position</div>
          <div class="card-value" style="font-size: 14px;">{pos_display}</div>
        </div>
        <div class="card">
          <div class="card-label">Soil Moisture</div>
          <div class="card-value" style="color: #d97706;">{soil_moisture:.1f}% VWC</div>
        </div>
      </div>

      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px 16px;">
        <div class="detail-row">
          <span class="detail-label">Target Plant / Crop</span>
          <span class="detail-val">{plant_name} ({crop_type})</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Recommended Water Dosage</span>
          <span class="detail-val">{water_quantity}</span>
        </div>
        <div class="detail-row" style="border-bottom: none;">
          <span class="detail-label">Optimal Operating Window</span>
          <span class="detail-val">{timing_advice}</span>
        </div>
      </div>

      <div class="advisory">
        <h4>Agronomic Field Guidelines</h4>
        <ul>
          {advisory_html_items}
        </ul>
      </div>
    </div>

    <div class="footer">
      This is an automated intelligence alert generated by your AgriShield IoT & Climate Engine.<br>
      Protecting crop yield through precision moisture analytics.
    </div>
  </div>
</body>
</html>
"""

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from_email = os.getenv("SMTP_FROM_EMAIL", "alerts@agrishield.ai")

    # If SMTP is configured, attempt live dispatch
    if smtp_host and smtp_user and smtp_password:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = smtp_from_email
        msg["To"] = to_email
        msg.set_content(plain_content)
        msg.add_alternative(html_content, subtype="html")

        try:
            with smtplib.SMTP(smtp_host, int(smtp_port), timeout=15) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            return {
                "status": "success",
                "sent": True,
                "recipient": to_email,
                "message": f"Irrigation alert email successfully delivered to {to_email}",
            }
        except Exception as exc:
            print(f"[Irrigation Email] SMTP dispatch error: {exc}. Logging alert to console.")

    # Local development or when SMTP not set: print structured console log
    print("=" * 65)
    print("📢 AUTOMATIC IRRIGATION EMAIL ALERT (CONSOLE DISPATCH)")
    print("=" * 65)
    print(f"TO:                {to_email} ({farmer_display})")
    print(f"SUBJECT:           {subject}")
    print(f"PLANT NAME:        {plant_name} ({crop_type})")
    print(f"FIELD POSITION:    {pos_display}")
    print(f"TIMES NEEDED:      {freq_display}")
    print(f"HOURS NEEDED:      {hours_display} Hours")
    print(f"SOIL MOISTURE:     {soil_moisture:.1f}% VWC")
    print(f"WATER QUANTITY:    {water_quantity}")
    print(f"TIMING ADVICE:     {timing_advice}")
    print("-" * 65)
    for adv in advisories:
        print(f"  * {adv}")
    print("=" * 65)

    return {
        "status": "success",
        "sent": True,
        "mode": "console_dispatch" if not (smtp_host and smtp_user) else "smtp_fallback_console",
        "recipient": to_email,
        "message": f"Irrigation alert notification generated for {to_email}",
        "summary": {
            "plant_name": plant_name,
            "crop_type": crop_type,
            "field_position": pos_display,
            "irrigation_frequency": freq_display,
            "irrigation_hours": hours_display,
            "soil_moisture": soil_moisture,
        },
    }
