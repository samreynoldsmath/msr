"""
This was entirely written by ChatGPT because I can't be bothered
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os

# Path to the directory containing your PNG images
image_directory = "figs/n7"

# Output PDF file name
output_pdf = "output.pdf"

# Create a PDF document
c = canvas.Canvas(output_pdf, pagesize=letter)

# Get a list of all PNG files in the directory
image_files = [f for f in os.listdir(image_directory) if f.endswith('.png')]

# Set the dimensions for each image
image_width = 200  # Change this as needed
image_height = 150  # Change this as needed

# Set the initial position for placing images
x = 50
y = 650

# Loop through the image files and add them to the PDF
for image_file in image_files:
    image_path = os.path.join(image_directory, image_file)
    c.drawImage(ImageReader(image_path), x, y, width=image_width, height=image_height)

    # Move the position for the next image
    x += image_width + 20

    # Move to the next row if needed
    if x + image_width > letter[0] - 50:
        x = 50
        y -= image_height + 20
        if y < 50:
            c.showPage()  # Add a new page if the current page is full
            x = 50
            y = 650

# Save the PDF
c.save()

print(f"PDF created: {output_pdf}")
