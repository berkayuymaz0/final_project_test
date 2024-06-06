from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from datetime import datetime

def generate_report(analysis_results, ai_suggestions, report_title="Security Analysis Report", output_dir="."):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"security_analysis_report_{timestamp}.pdf"
    report_path = os.path.join(output_dir, report_filename)
    
    try:
        c = canvas.Canvas(report_path, pagesize=letter)
        width, height = letter

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2.0, height - 50, report_title)

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
    except Exception as e:
        raise RuntimeError(f"Error generating report: {e}")

# Example usage:
# analysis_results = "Example analysis results text..."
# ai_suggestions = "Example AI suggestions text..."
# report_path = generate_report(analysis_results, ai_suggestions)
# print(f"Report generated: {report_path}")
