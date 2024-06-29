from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_report(analysis_results, ai_suggestions, report_title="Security Analysis Report", output_dir="."):
    """
    Generate a PDF report with analysis results and AI suggestions.
    
    :param analysis_results: A string containing the analysis results.
    :param ai_suggestions: A string containing the AI suggestions.
    :param report_title: The title of the report.
    :param output_dir: The directory where the report will be saved.
    :return: The path to the generated report.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"security_analysis_report_{timestamp}.pdf"
    report_path = os.path.join(output_dir, report_filename)
    
    try:
        c = canvas.Canvas(report_path, pagesize=letter)
        width, height = letter

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2.0, height - 50, report_title)

        # Add Analysis Results
        _add_text_to_canvas(c, "Analysis Results:", analysis_results, height - 100)

        # Add AI Suggestions
        _add_text_to_canvas(c, "AI Suggestions:", ai_suggestions, height - 200)

        c.save()
        logger.info(f"Report generated: {report_path}")
        return report_path
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise RuntimeError(f"Error generating report: {e}")

def _add_text_to_canvas(canvas_obj, header, text, start_y, line_height=15, page_margin=50):
    """
    Add a block of text to the canvas with a header, handling page breaks.
    
    :param canvas_obj: The canvas object to draw on.
    :param header: The header for the text block.
    :param text: The text content to add.
    :param start_y: The starting y-coordinate on the canvas.
    :param line_height: The height of each line of text.
    :param page_margin: The margin to leave at the bottom of the page before a page break.
    """
    width, height = letter
    canvas_obj.setFont("Helvetica-Bold", 12)
    canvas_obj.drawString(50, start_y, header)
    canvas_obj.setFont("Helvetica", 10)
    
    y = start_y - 20
    for line in text.split('\n'):
        canvas_obj.drawString(50, y, line)
        y -= line_height
        if y < page_margin:
            canvas_obj.showPage()
            canvas_obj.setFont("Helvetica", 10)
            y = height - page_margin

# Example usage:
# analysis_results = "Example analysis results text..."
# ai_suggestions = "Example AI suggestions text..."
# report_path = generate_report(analysis_results, ai_suggestions)
# print(f"Report generated: {report_path}")
