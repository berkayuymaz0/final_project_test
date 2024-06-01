from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def generate_report(analysis_results, ai_suggestions):
    report_path = "security_analysis_report.pdf"
    c = canvas.Canvas(report_path, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2.0, height - 50, "Security Analysis Report")

    # Analysis Results
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 100, "Analysis Results:")
    c.setFont("Helvetica", 10)
    
    y = height - 120
    for line in analysis_results.split('\n'):
        c.drawString(50, y, line)
        y -= 15
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 50
    
    # AI Suggestions
    c.setFont("Helvetica-Bold", 12)
    y -= 30
    c.drawString(50, y, "AI Suggestions:")
    c.setFont("Helvetica", 10)
    y -= 20
    
    for line in ai_suggestions.split('\n'):
        c.drawString(50, y, line)
        y -= 15
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 50

    c.save()
    return report_path
