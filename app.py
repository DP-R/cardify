import os, sys
if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))

import os
import fitz
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename

from rc_converter import parse_rc_a4, generate_rc_card
from dl_converter import parse_dl_a4, generate_dl_card

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32 MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def detect_doc_type(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
        
    if "FORM 6" in text.upper() or "DRIVING LICENCE" in text.upper():
        return "dl"
    elif "FORM 23" in text.upper() or "CERTIFICATE OF REGISTRATION" in text.upper() or "REGISTRATION" in text.upper():
        return "rc"
    else:
        return "rc" # default fallback


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    doc_type = request.form.get('doc_type', 'auto')
    
    filename = secure_filename(file.filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(upload_path)
    
    if doc_type == 'auto':
        doc_type = detect_doc_type(upload_path)
        
    output_filename = f"converted_{doc_type}_{filename}"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    try:
        if doc_type == 'rc':
            data = parse_rc_a4(upload_path)
            generate_rc_card(data, output_path)
            summary = {
                "Document Type": "Vehicle Registration Certificate (RC)",
                "Regn Number": data.get("reg_no"),
                "Owner Name": data.get("owner_name"),
                "Regn Date": data.get("reg_date"),
                "Validity": data.get("valid_upto"),
                "Vehicle Class": data.get("vehicle_class"),
                "Maker Name": data.get("maker_name"),
                "Model Name": data.get("model_name"),
                "Chassis No": data.get("chassis_no"),
                "Engine No": data.get("engine_no")
            }
        else: # dl
            data = parse_dl_a4(upload_path)
            generate_dl_card(data, output_path)
            summary = {
                "Document Type": "Driving Licence (DL)",
                "DL Number": data.get("dl_no"),
                "Holder Name": data.get("name"),
                "Father's Name": data.get("swd_of"),
                "Date of Birth": data.get("dob"),
                "Issue Date": data.get("issue_date"),
                "NT Validity": data.get("validity_nt"),
                "Original LA": data.get("original_la")
            }
            
        # Also render PNG screenshots of output PDF pages for live web preview
        doc_out = fitz.open(output_path)
        preview_imgs = []
        for i, page in enumerate(doc_out):
            pix = page.get_pixmap(dpi=200)
            img_name = f"preview_{doc_type}_{i+1}_{filename[: -4]}.png"
            img_path = os.path.join('static', 'previews', img_name)
            os.makedirs(os.path.dirname(img_path), exist_ok=True)
            pix.save(img_path)
            preview_imgs.append(f"/static/previews/{img_name}")
            
        return jsonify({
            'success': True,
            'doc_type': doc_type,
            'download_url': f'/download/{output_filename}',
            'previews': preview_imgs,
            'summary': summary
        })
        
    except Exception as e:
        import traceback; traceback.print_exc(); return jsonify({"error": str(e)}), 500


@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404


if __name__ == '__main__':
    import os
    if os.environ.get("FLASK_SERVER_ONLY") == "1":
        print("Starting Card Converter Web App server on http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        from flaskwebgui import FlaskUI
        print("Starting Card Converter Desktop App...")
        FlaskUI(app=app, server="flask", port=5000, width=1200, height=800).run()
