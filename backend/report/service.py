import io
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def generate_prediction_report(prediction_id: int):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("<b>AgriShield AI Prediction Report</b>", styles["Title"]))

    elements.append(Paragraph(f"Prediction ID: {prediction_id}", styles["BodyText"]))

    elements.append(Paragraph("Crop: Cotton", styles["BodyText"]))

    elements.append(Paragraph("Predicted Pest Value: 32.45", styles["BodyText"]))

    elements.append(Paragraph("Risk Level: Medium", styles["BodyText"]))

    elements.append(Paragraph(
        "Recommendation: Monitor crop every 2 days and use pheromone traps.",
        styles["BodyText"],
    ))

    doc.build(elements)

    buffer.seek(0)

    return buffer