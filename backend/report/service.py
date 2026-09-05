import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from sqlalchemy.orm import Session

from history.models import PredictionHistory
from recommendation.service import _match_pest_rules, _URGENCY_BY_RISK


def generate_prediction_report(db: Session, prediction_id: int):
    record = (
        db.query(PredictionHistory)
        .filter(PredictionHistory.id == prediction_id)
        .first()
    )

    if not record:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#166534"),
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#4B5563"),
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#166534"),
        spaceBefore=8,
        spaceAfter=4,
    )
    cell_label = ParagraphStyle(
        "CellLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#374151"),
    )
    cell_val = ParagraphStyle(
        "CellValue",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#111827"),
    )
    risk_title_style = ParagraphStyle(
        "RiskTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        alignment=1,  # Center
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#374151"),
    )

    elements = []

    # 1. Header Banner
    elements.append(Paragraph("AgriShield AI — Pest Intelligence Report", title_style))
    elements.append(Paragraph("Predictive Pest Outbreak Intelligence & Crop Protection Advisory", subtitle_style))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#166534"), spaceAfter=12))

    # 2. Risk Level Card
    risk_color_map = {
        "High": (colors.HexColor("#DC2626"), colors.HexColor("#FEF2F2")),
        "Medium": (colors.HexColor("#D97706"), colors.HexColor("#FFFBEB")),
        "Low": (colors.HexColor("#16A34A"), colors.HexColor("#F0FDF4")),
    }
    risk_text_color, risk_bg = risk_color_map.get(
        record.risk_level, (colors.HexColor("#16A34A"), colors.HexColor("#F0FDF4"))
    )

    risk_card_data = [
        [
            Paragraph(f"<b>RISK LEVEL: {record.risk_level.upper()}</b>", ParagraphStyle(
                "RiskH", fontName="Helvetica-Bold", fontSize=14, leading=16, textColor=risk_text_color, alignment=1
            )),
            Paragraph(f"<b>Predicted Pest Score: {record.pest_value:.1f}</b>", ParagraphStyle(
                "RiskScore", fontName="Helvetica-Bold", fontSize=14, leading=16, textColor=colors.HexColor("#111827"), alignment=1
            )),
        ]
    ]
    risk_table = Table(risk_card_data, colWidths=[270, 270])
    risk_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), risk_bg),
        ("BOX", (0, 0), (-1, -1), 1.5, risk_text_color),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(risk_table)
    elements.append(Spacer(1, 12))

    # 3. Field & Prediction Information
    elements.append(Paragraph("1. Field & Prediction Parameters", section_heading))
    
    date_str = record.prediction_date.strftime("%Y-%m-%d %H:%M UTC") if isinstance(record.prediction_date, datetime) else str(record.prediction_date)
    field_info = [
        [
            Paragraph("Report ID:", cell_label), Paragraph(f"#{record.id}", cell_val),
            Paragraph("Crop:", cell_label), Paragraph(str(record.crop), cell_val),
        ],
        [
            Paragraph("Target Pest:", cell_label), Paragraph(str(record.pest_name), cell_val),
            Paragraph("Location:", cell_label), Paragraph(str(record.location), cell_val),
        ],
        [
            Paragraph("Observation Year:", cell_label), Paragraph(str(record.observation_year or "—"), cell_val),
            Paragraph("Standard Week:", cell_label), Paragraph(f"Week {record.standard_week or '—'}", cell_val),
        ],
        [
            Paragraph("Generated Date:", cell_label), Paragraph(date_str, cell_val),
            Paragraph("Status:", cell_label), Paragraph("Verified by AI Model", cell_val),
        ],
    ]
    t_field = Table(field_info, colWidths=[100, 170, 100, 170])
    t_field.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F9FAFB")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_field)
    elements.append(Spacer(1, 10))

    # 4. Environmental & Meteorological Data
    elements.append(Paragraph("2. Environmental & Weather Conditions", section_heading))
    weather_info = [
        [
            Paragraph("Max Temperature (MaxT):", cell_label),
            Paragraph(f"{record.max_t} °C" if record.max_t is not None else "—", cell_val),
            Paragraph("Min Temperature (MinT):", cell_label),
            Paragraph(f"{record.min_t} °C" if record.min_t is not None else "—", cell_val),
        ],
        [
            Paragraph("Morning Humidity (RH1):", cell_label),
            Paragraph(f"{record.rh1} %" if record.rh1 is not None else "—", cell_val),
            Paragraph("Evening Humidity (RH2):", cell_label),
            Paragraph(f"{record.rh2} %" if record.rh2 is not None else "—", cell_val),
        ],
        [
            Paragraph("Rainfall (RF):", cell_label),
            Paragraph(f"{record.rf} mm" if record.rf is not None else "—", cell_val),
            Paragraph("Wind Speed (WS):", cell_label),
            Paragraph(f"{record.ws} km/h" if record.ws is not None else "—", cell_val),
        ],
        [
            Paragraph("Sunshine Duration (SSH):", cell_label),
            Paragraph(f"{record.ssh:.1f} hrs" if record.ssh is not None else "—", cell_val),
            Paragraph("Evapotranspiration (EVP):", cell_label),
            Paragraph(f"{record.evp} mm" if record.evp is not None else "—", cell_val),
        ],
    ]
    t_weather = Table(weather_info, colWidths=[150, 120, 150, 120])
    t_weather.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F9FAFB")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_weather)
    elements.append(Spacer(1, 10))

    # 5. Agronomic Recommendations & Treatment Plan
    rules = _match_pest_rules(record.pest_name)
    urgency = _URGENCY_BY_RISK.get(record.risk_level, _URGENCY_BY_RISK["Medium"])
    yield_loss = rules["yield_impact"].get(record.risk_level, rules["yield_impact"]["Medium"])

    elements.append(Paragraph("3. Agronomic Advisory & Integrated Pest Management (IPM)", section_heading))
    
    recom_text = f"<b>Urgency:</b> {urgency}. Expected Potential Yield Impact: <b>{yield_loss}%</b> if left unmanaged."
    elements.append(Paragraph(recom_text, body_style))
    elements.append(Spacer(1, 4))

    actions_str = "<br/>• ".join(["• " + a for a in rules["actions"]])
    organic_str = "<br/>• ".join(["• " + o for o in rules["organic"]])
    pesticide_str = "<br/>• ".join(["• " + p for p in rules["pesticides"]])

    rec_table_data = [
        [Paragraph("<b>Suggested Actions:</b>", cell_label), Paragraph(actions_str, body_style)],
        [Paragraph("<b>Organic Remedies:</b>", cell_label), Paragraph(organic_str, body_style)],
        [Paragraph("<b>Targeted Pesticides:</b>", cell_label), Paragraph(pesticide_str, body_style)],
    ]
    t_rec = Table(rec_table_data, colWidths=[130, 410])
    t_rec.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F9FAFB")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(t_rec)
    elements.append(Spacer(1, 12))

    # 6. Disclaimer Footer
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D1D5DB"), spaceAfter=6))
    elements.append(Paragraph(
        "<i>Disclaimer: AgriShield AI predictions are driven by multi-season machine learning models and meteorological data. "
        "Always cross-examine field conditions and consult local agricultural extension officers before heavy chemical application.</i>",
        ParagraphStyle("Discl", fontName="Helvetica-Oblique", fontSize=7.5, leading=10, textColor=colors.HexColor("#6B7280"))
    ))

    doc.build(elements)
    buffer.seek(0)

    return buffer