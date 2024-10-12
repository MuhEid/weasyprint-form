import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from weasyprint import HTML
from jinja2 import Template
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="http://localhost:3000")  # Allow all routes from this origin

# Output directory for PDFs
output_dir = './pdfs'
os.makedirs(output_dir, exist_ok=True)

# Increase the recursion limit if necessary
sys.setrecursionlimit(5000)

@app.route('/api/submit', methods=['POST'])
def submit():
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid content type, expected application/json"}), 400
        data = request.get_json()

        print('Received values:', data)

        # Read the HTML template
        try:
            with open('./test.html', 'r', encoding='utf-8') as file:
                template = Template(file.read())
        except Exception as e:
            print("Error reading template:", e)
            return jsonify({"error": "Template file not found or unreadable."}), 500

        html_content = template.render(data).encode( "utf-8" )


        # Generate PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_pdf_file = os.path.join(output_dir, f'output_{data["orderId"]}_{timestamp}.pdf')
        HTML(string=html_content, base_url='.', encoding='utf-8').write_pdf(output_pdf_file)

        # Send the download URL
        download_url = f"/pdfs/{os.path.basename(output_pdf_file)}"
        return jsonify({
                "submission_text": "Thank you for your submission",
                "redirect_url": None,
                "errors": [],
                "download_url": download_url,
            }), 200

    except Exception as e:
        print("Error in /api/submit:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/pdfs/<filename>', methods=['GET'])
def download_pdf(filename):
    try:
        return send_from_directory(output_dir, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)
