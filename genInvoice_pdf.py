from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import utils
from datetime import datetime

def generate_pdf_invoice(hourly_rate, num_hours, client_name, invoice_date, start_period_date, end_period_date, image_file):
    # Create a filename based on current timestamp
    filename = f"invoice_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

    # Prepare data
    invoice_number = "000014"  # You might want to generate this dynamically
    subtotal = hourly_rate * num_hours
    total_due = subtotal

    # Image
    img = utils.ImageReader(image_file)
    width, height = img.getSize()
    aspect = height / width
    logo = Image(image_file, width=2*inch, height=(2*inch)*aspect)

    # Styles
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading1"]
    body_style = styles["BodyText"]
    right_alignment_style = ParagraphStyle(name="right_alignment", parent=body_style, alignment=TA_RIGHT)

    # Content
    content = []

    # Header
    content.append(logo)
    content.append(Paragraph("O3 Ventures", title_style))
    content.append(Paragraph("Invoice Sent", heading_style))
    content.append(Spacer(1, 12))

    # Invoice Summary
    content.append(Paragraph(f"${total_due:.2f}", heading_style))
    content.append(Paragraph(f"Due on {invoice_date.strftime('%B %d, %Y')}", heading_style))
    content.append(Spacer(1, 12))

    # Customer Information
    content.append(Paragraph("Customer", heading_style))
    customer_info = [
        ["Dijoy Divakaran"],
        ["InKind"],
        ["ap@inkind.com"],
        ["870-273-8473"],
        ["600 Congress Ave."],
        ["Suite 1700"],
        ["Austin, TX 78701"]
    ]
    t = Table(customer_info)
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    content.append(t)
    content.append(Spacer(1, 12))

    # Date of Service
    content.append(Paragraph("Date of service", heading_style))
    content.append(Paragraph(f"{start_period_date.strftime('%B %d, %Y')}", body_style))
    content.append(Spacer(1, 12))

    # Message
    content.append(Paragraph("Download Invoice PDF", body_style))
    content.append(Paragraph("O3 Ventures", body_style))
    content.append(Paragraph("21 Sycamore Drive", body_style))
    content.append(Paragraph("Roslyn, NY 11576", body_style))
    content.append(Spacer(1, 12))

    # Invoice Summary
    content.append(Paragraph("Invoice summary", heading_style))
    summary_info = [
        ["Technology Services - Nishant V", f"${subtotal:.2f}", f"(${hourly_rate:.2f}/hr) x {num_hours:.2f} hr"],
        ["Technology Services - Kalyan J", f"${subtotal:.2f}", f"(${hourly_rate:.2f}/hr) x {num_hours:.2f} hr"]
    ]
    t = Table(summary_info)
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    content.append(t)
    content.append(Spacer(1, 12))

    # Subtotal
    content.append(Paragraph(f"Subtotal: ${subtotal:.2f}", right_alignment_style))
    # Total Due
    content.append(Paragraph(f"Total Due: ${total_due:.2f}", right_alignment_style))

    # Create PDF
    doc = SimpleDocTemplate(filename, pagesize=letter)
    doc.build(content)

    return filename

# Test the function
hourly_rate = 37.0
num_hours = 176.0
client_name = "Dijoy Divakaran"
invoice_date = datetime(2024, 5, 17)
start_period_date = datetime(2024, 4, 30)
end_period_date = datetime(2024, 4, 30)
image_file = "rayze_logo.jpg"  # Change this to the path of your logo image
pdf_filename = generate_pdf_invoice(hourly_rate, num_hours, client_name, invoice_date, start_period_date, end_period_date, image_file)
print("PDF invoice generated:", pdf_filename)
