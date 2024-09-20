from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf(order):
    pdf_file = BytesIO()
    p = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter
    
    p.drawString(100, height - 100, f"Invoice for Order #{order.id}")
    p.drawString(100, height - 120, "Thank you for your purchase!")
    
    y_position = height - 150
    p.drawString(100, y_position, "Order Details:")
    y_position -= 20
    p.drawString(100, y_position, "Item                         Price")
    
    total_price = 0.00  # Initialize total price

    for item in order.items.all():
        y_position -= 20
        p.drawString(100, y_position, f"{item.name:<30} ${item.price:.2f}")
        total_price += float(item.price)  # Convert Decimal to float before adding
    
    # Update the total in the order object if needed
    order.total = total_price
    order.save()

    y_position -= 20
    p.drawString(100, y_position, f"Total: ${total_price:.2f}")
    
    p.showPage()
    p.save()
    pdf_file.seek(0)
    
    return pdf_file
