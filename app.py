import os
import sys
import smtplib
from flask import Flask, request, jsonify, send_from_directory
from weasyprint import HTML
from jinja2 import Template
from datetime import datetime
from flask_cors import CORS
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv() 
app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": [
            "http://localhost:3000",
            "http://178.254.29.140:3000",
            "https://www.handytechs.de"
        ]}}
)

# Output directory for PDFs
output_dir = './pdfs'
os.makedirs(output_dir, exist_ok=True)

SMTP_SERVER   = os.getenv("SMTP_SERVER", "smtp.1blu.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", 465))
SMTP_USERNAME = os.getenv("EMAIL_USER")
SMTP_PASSWORD = os.getenv("EMAIL_PASS")
SENDER_EMAIL  = os.getenv("EMAIL_ADDRESS")

# Increase the recursion limit if necessary
sys.setrecursionlimit(5000)

@app.route('/api/submit', methods=['POST'])
def submit():
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid content type, expected application/json"}), 400
        data = request.get_json()
        data["timestamp"] = datetime.now().strftime("%Y-%m-%d")

        # Read the HTML template
        try:
            with open('./test.html', 'r', encoding='utf-8') as file:
                template = Template(file.read())
        except Exception as e:
            print("Error reading template:", e)
            return jsonify({"error": "Template file not found or unreadable."}), 500

        html_content = template.render(data).encode( "utf-8" )


        # Generate PDF
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'output_{data["orderId"]}_{ts}.pdf'
        pdf_path = os.path.join(output_dir, filename)
        HTML(string=html_content, base_url='.', encoding='utf-8').write_pdf(pdf_path)

        # Send the download URL
        download_url = f"/pdfs/{os.path.basename(pdf_path)}"
        return jsonify({
                "submission_text": "Thank you for your submission",
                "redirect_url": None,
                "errors": [],
                "download_url": download_url,
                "filename":filename
            }), 200

    except Exception as e:
        print("Error in /api/submit:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/pdfs/<filename>', methods=['GET'])
def download_pdf(filename):
    try:
        return send_from_directory(output_dir, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@app.route('/api/send-email', methods=['POST'])
def send_email():
    """
    POST JSON:
    {
      "to":      "recipient@example.com",
      "subject": "Your repair order PDF",
      "formData": { ... same fields as before ... },
      "filename": "output_order123_20250513_150501.pdf"
    }
    """
    try:
        req = request.get_json()
        to_addr  = req.get("to")
        subject  = req.get("subject")
        formData = req.get("formData")
        filename = req.get("filename")

        # basic validation
        if not all([to_addr, subject, formData, filename]):
            return jsonify({"error": "Missing required field"}), 400

        # load & render email template
        tpl_path = os.path.join("templates", "emailTemplate.html")
        try:
            with open(tpl_path, 'r', encoding='utf-8') as f:
                tpl = Template(f.read())
        except Exception as e:
            print("Template load error:", e)
            return jsonify({"error": "Email template not found."}), 500

        html_body = tpl.render(**formData)

        # prepare email
        msg = EmailMessage()
        msg["From"]    = f"PhonyTechs Support <{SENDER_EMAIL}>"
        msg["To"]      = to_addr
        msg["Subject"] = subject
        msg.set_content("Your email client does not support HTML.")
        msg.add_alternative(html_body, subtype="html")

        # attach PDF
        pdf_path = os.path.join(output_dir, filename)
        if not os.path.isfile(pdf_path):
            return jsonify({"error": "PDF file not found"}), 404

        with open(pdf_path, "rb") as pdf:
            msg.add_attachment(
                pdf.read(),
                maintype="application",
                subtype="pdf",
                filename=filename
            )

        # send via SSL (port 465)
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.set_debuglevel(1)
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(msg)

        return jsonify({"message": "Email sent successfully"}), 200

    except Exception as e:
        print("Error in /api/send-email:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
