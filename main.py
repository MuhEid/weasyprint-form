import os
import sys
from weasyprint import HTML

# URL of the local web page you want to convert to PDF
local_web_page_url = 'http://localhost:3000/form'

# Output PDF file name
output_pdf_file = './output.pdf'

def create_pdf_from_local_web_page(url, output_file):
    try:
        # Increase the recursion limit
        sys.setrecursionlimit(5000)
        print('hhhhhhhhhhhhhhhhhhhhh')
        # Generate the PDF
        HTML('./index.html').write_pdf(output_file)
        print(f"PDF created successfully: {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_pdf_from_local_web_page(local_web_page_url, output_pdf_file)
