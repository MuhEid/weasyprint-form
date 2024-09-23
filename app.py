import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from weasyprint import HTML
from jinja2 import Template
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Output directory for PDFs
output_dir = './pdfs'
os.makedirs(output_dir, exist_ok=True)

# Increase the recursion limit
sys.setrecursionlimit(5000)

@app.route('/api/submit', methods=['POST'])
def submit():
    try:
         # Step 1: Receive the dictionary named values
         
        if not request.is_json:
            return jsonify({"error": "Invalid content type, expected application/json"}), 400
        data = request.get_json()
       
        print('Received values:', data)
        
        # Step 2: Insert values into the local HTML template
        
        try:
            with open('./template.html', 'r') as file:
                template = Template(file.read())
        except Exception as e:
            print(e)
        html_content = template.render(data)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_pdf_file = os.path.join(output_dir, f'output_{data["orderId"]}_{timestamp}.pdf')
        HTML(string=html_content, base_url='.', encoding='utf-8').write_pdf(output_pdf_file)

        # Step 4: Send the download URL for this PDF file back to the user
        download_url = f"/pdfs/output.pdf"
        return jsonify({
                "submission_text": "Thank you for your submission",
                "redirect_url": None,
                "errors": [],
                "download_url": download_url,
            },
           ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pdfs/<filename>', methods=['GET'])
def download_pdf(filename):
    try:
        return send_from_directory(output_dir, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(host='localhost', port=5000)
