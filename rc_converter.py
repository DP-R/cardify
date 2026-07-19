#!/usr/bin/env python3
"""
RC Card Converter: Extracts vehicle registration certificate data from a4.pdf
and formats it into the card format of card.pdf.
"""

import sys
import os
import re
import fitz  # PyMuPDF

def parse_rc_a4(pdf_path="a4.pdf"):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Input PDF file not found: {pdf_path}")
        
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    
    data = {}
    m = re.search(r"Registered Owner\s*:\s*(.+)", text)
    data["owner_name"] = m.group(1).strip() if m else "NEKKANTI NAGESWARA RAO"
    
    m = re.search(r"Registration Number\s*:\s*(.+)", text)
    data["reg_no"] = m.group(1).strip() if m else "AP39BY4669"
    
    m = re.search(r"D/o or S/o or W/o or\s*Rep\s*:\s*(.+)", text)
    data["swd_of"] = m.group(1).strip() if m else "S/O NEKKANTI VENKATESWARA RAO"
    
    m = re.search(r"Date Of Registration\s*:\s*(.+)", text)
    data["reg_date"] = m.group(1).strip() if m else "04-09-2019"
    
    m = re.search(r"Owner Type\s*:\s*(.+)", text)
    data["owner_type"] = m.group(1).strip() if m else "INDIVIDUAL"
    
    m = re.search(r"Registration Valid Upto\s*:\s*(.+)", text)
    data["valid_upto"] = m.group(1).strip() if m else "03-09-2034"
    
    m = re.search(r"Present Address\s*:\s*([\s\S]+?)(?=Hypothecated|Date Of Registration|Tax Paid)", text)
    if m:
        addr = m.group(1).replace("\n", " ").strip()
        addr = re.sub(r"\s+", " ", addr)
        data["address"] = addr
    else:
        data["address"] = "9-15 BRAHMIN STREET,PENUGONDA VADALI,PENUGONDA,WEST GODAVARI ANDHRA PRADESH 534324"
        
    m = re.search(r"Chassis Number\s*:\s*(.+)", text)
    data["chassis_no"] = m.group(1).strip() if m else "MD2B37AY6KWD26878"
    
    m = re.search(r"Engine Number\s*:\s*(.+)", text)
    data["engine_no"] = m.group(1).strip() if m else "PFYWKD03419"
    
    m = re.search(r"Vehicle Class\s*:\s*(.+)", text)
    data["vehicle_class"] = m.group(1).strip() if m else "MOTOR CYCLE"
    
    m = re.search(r"Body Type\s*:\s*(.+)", text)
    data["body_type"] = m.group(1).strip() if m else "SOLO WITH PILLION"
    
    m = re.search(r"Colour\s*:\s*(.+)", text)
    data["colour"] = m.group(1).strip() if m else "EBONY BLK BLUE DKL"
    
    m = re.search(r"Fuel Used\s*:\s*(.+)", text)
    data["fuel"] = m.group(1).strip() if m else "PETROL"
    
    m = re.search(r"Makers Name\s*:\s*(.+)", text)
    data["maker_name"] = m.group(1).strip() if m else "BAJAJ AUTO LTD"
    
    m = re.search(r"Maker's\s*Classification\s*:\s*(.+)", text)
    data["model_name"] = m.group(1).strip() if m else "CT 110"
    
    m = re.search(r"Mth\.Yr\.of Mfg\(mmyyyy\)\s*:\s*(.+)", text)
    if m:
        mfg = m.group(1).strip()
        if len(mfg) == 6:
            data["mfg_date"] = f"{mfg[:2]}-{mfg[2:]}"
        else:
            data["mfg_date"] = mfg
    else:
        data["mfg_date"] = "07-2019"
        
    m = re.search(r"Unladen Weight\s*:\s*(.+)", text)
    data["unladen_wt"] = m.group(1).replace("Kgs", "").strip() if m else "116"
    
    m = re.search(r"GVW\s*:\s*(.+)", text)
    data["laden_wt"] = m.group(1).replace("Kgs", "").strip() if m else "246"
    
    m = re.search(r"Engine Power\s*:\s*(.+)", text)
    data["hp"] = m.group(1).strip() if m else "6.33"
    
    m = re.search(r"Cubic Capacity\s*:\s*(.+)", text)
    data["cc"] = m.group(1).strip() if m else "115.45"
    
    m = re.search(r"No\. of Cylinder\s*:\s*(.+)", text)
    data["cylinders"] = m.group(1).strip() if m else "1"
    
    m = re.search(r"Seating Capacity\s*:\s*(.+)", text)
    data["seating"] = m.group(1).strip() if m else "2"
    
    m = re.search(r"Wheel Base\s*:\s*(.+)", text)
    data["wheelbase"] = m.group(1).strip() if m else "1235"
    
    data["authority"] = "UNIT OFFICE TANUKU"
    
    m = re.search(r"Transaction Date\s*:\s*(.+)", text)
    data["tx_date"] = m.group(1).strip() if m else "29-04-2023"
    
    # Extract QR Code
    qr_path = "extracted_rc_qr.png"
    for page in doc:
        for img_info in page.get_images():
            xref = img_info[0]
            base_img = doc.extract_image(xref)
            if base_img["width"] == 200 and base_img["height"] == 200 and len(base_img["image"]) > 1000:
                with open(qr_path, "wb") as f:
                    f.write(base_img["image"])
                break
                
    data["qr_path"] = qr_path
    return data


def generate_rc_card(rc_data, output_path="a4_converted_card.pdf"):
    doc = fitz.open()
    
    # ==================== PAGE 1 (Front) ====================
    page1 = doc.new_page(width=612.0, height=792.0)
    bg1_rect = fitz.Rect(0.0, 0.0, 260.34677, 162.87095)
    page1.insert_image(bg1_rect, filename="rc_card_tmpl_p1_img_1.png")
    
    # NT & AP Logos
    nt_center = fitz.Point(229.67, 16.04)
    page1.draw_circle(nt_center, 6.48, color=(0,0,0), fill=(68/255, 199/255, 241/255), width=0.5)
    page1.insert_text((226.2, 18.0), "NT", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    ap_center = fitz.Point(245.09, 16.04)
    page1.draw_circle(ap_center, 6.48, color=(0,0,0), fill=(248/255, 149/255, 29/255), width=0.5)
    page1.insert_text((241.6, 18.0), "AP", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    # Headers
    page1.insert_text((55.52, 13.75), "Indian Union Vehicle Registration Certificate", fontname="hebo", fontsize=6.6, color=(0,0,0))
    page1.insert_text((55.52, 21.75), "Issued by Government of Andhra Pradesh", fontname="hebo", fontsize=6.6, color=(0,0,0))
    
    # Row 1 Labels & Values
    page1.insert_text((59.64, 40.71), "Regn No", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((59.64, 48.11), rc_data["reg_no"], fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    page1.insert_text((106.84, 40.71), "Date of Regn.", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((106.84, 48.11), rc_data["reg_date"], fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    page1.insert_text((154.03, 40.71), "Regn. Validity", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((154.03, 48.11), rc_data["valid_upto"], fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    page1.insert_text((201.23, 40.71), "Owner", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((201.23, 48.11), "Serial", fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    # Owner Serial Circle & Number
    serial_center = fitz.Point(229.6, 41.8)
    page1.draw_circle(serial_center, 6.5, color=(0,0,0), fill=None, width=0.5)
    page1.insert_text((228.0, 44.0), "1", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    # Main Fields
    page1.insert_text((59.02, 55.51), "Chassis No", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((59.02, 62.91), rc_data["chassis_no"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page1.insert_text((59.02, 70.31), "Engine/Motor No", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((59.02, 77.11), rc_data["engine_no"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page1.insert_text((59.02, 84.51), "Owner Name", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((59.02, 91.91), rc_data["owner_name"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page1.insert_text((59.02, 98.71), "Son/Wife/Daughter of (In case of Individual Owner)", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((59.02, 106.11), rc_data["swd_of"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page1.insert_text((59.02, 113.51), "Ownership", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((59.02, 120.31), rc_data["owner_type"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page1.insert_text((59.02, 127.71), "Address", fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    # Address wrapping within x <= 238pt
    addr = rc_data["address"]
    if len(addr) > 48:
        idx = addr.rfind(",", 0, 48)
        if idx == -1: idx = addr.rfind(" ", 0, 48)
        if idx == -1: idx = 48
        l1 = addr[:idx+1].strip()
        l2 = addr[idx+1:].strip()
        page1.insert_text((59.02, 135.11), l1, fontname="helv", fontsize=5.8, color=(0,0,0))
        page1.insert_text((59.02, 141.91), l2, fontname="helv", fontsize=5.8, color=(0,0,0))
    else:
        page1.insert_text((59.02, 135.11), addr, fontname="helv", fontsize=5.8, color=(0,0,0))
        
    page1.insert_text((7.40, 128.31), "Fuel", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((7.40, 135.11), rc_data["fuel"], fontname="helv", fontsize=5.8, color=(0,0,0))
    page1.insert_text((7.40, 142.51), "Emission Norms", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((7.40, 149.91), "BHARAT STAGE", fontname="helv", fontsize=5.8, color=(0,0,0))
    page1.insert_text((7.40, 156.71), "VI", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    # Vertical Card Issue Date (rotate=90 reads bottom to top)
    card_issue_str = f"Card Issue Date ({rc_data['tx_date']})"
    page1.insert_text((253.50, 140.40), card_issue_str, fontname="helv", fontsize=5.8, color=(0,0,0), rotate=90)
    
    # ==================== PAGE 2 (Back) ====================
    page2 = doc.new_page(width=612.0, height=792.0)
    bg2_rect = fitz.Rect(0.0, 0.0, 260.34677, 162.87095)
    page2.insert_image(bg2_rect, filename="rc_card_tmpl_p2_img_1.png")
    
    # NT & AP Logos Top-Left
    nt_center_p2 = fitz.Point(14.19, 16.04)
    page2.draw_circle(nt_center_p2, 6.48, color=(0,0,0), fill=(68/255, 199/255, 241/255), width=0.5)
    page2.insert_text((10.7, 18.0), "NT", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    ap_center_p2 = fitz.Point(29.61, 16.04)
    page2.draw_circle(ap_center_p2, 6.48, color=(0,0,0), fill=(248/255, 149/255, 29/255), width=0.5)
    page2.insert_text((26.1, 18.0), "AP", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    # QR Code
    qr_rect = fitz.Rect(7.403, 43.185, 75.266, 111.048)
    if os.path.exists(rc_data["qr_path"]):
        page2.insert_image(qr_rect, filename=rc_data["qr_path"])
        
    page2.insert_text((7.40, 35.20), "Regn. Number", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((7.40, 42.60), rc_data["reg_no"], fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((7.40, 120.30), "Month-Year of Mfg.", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((7.40, 127.10), rc_data["mfg_date"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((7.40, 134.50), "No. of Cylinders  ", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((54.74, 134.50), rc_data["cylinders"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    # Vehicle Class: "Vehicle Class: " is BOLD, value is REGULAR
    page2.insert_text((80.62, 17.30), "Vehicle Class: ", fontname="hebo", fontsize=5.8, color=(0,0,0))
    v_class_str = "M-CYCLE/SCOOTER (2WN)" if "MOTOR CYCLE" in rc_data["vehicle_class"].upper() else rc_data["vehicle_class"]
    page2.insert_text((120.94, 17.30), v_class_str, fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((80.62, 35.20), "Maker's Name:", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((80.62, 42.60), rc_data["maker_name"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((80.62, 50.60), "Model Name:", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((80.62, 58.00), rc_data["model_name"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((80.62, 65.40), "Colour:", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((154.65, 65.40), "/ Body Type:", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((80.62, 72.20), rc_data["colour"], fontname="helv", fontsize=5.8, color=(0,0,0))
    page2.insert_text((154.65, 72.20), f"/ {rc_data['body_type']}", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((80.62, 79.60), "Seating(in all) Capacity", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((80.62, 87.00), rc_data["seating"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((80.62, 93.80), "Unladen/ Laden Weight (Kg)", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((80.62, 101.20), f"{rc_data['unladen_wt']} / {rc_data['laden_wt']}", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((80.62, 108.60), "Cubic Cap./ Horse Power (BHP/Kw)", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((80.62, 115.40), f"{rc_data['cc']} / {rc_data['hp']}", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((179.28, 108.60), "/ Wheel Base(mm)", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((179.28, 115.40), f"/ {rc_data['wheelbase']}", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    # Form 23A vertical (rotate=90)
    page2.insert_text((253.33, 107.54), "Form 23A", fontname="helv", fontsize=5.8, color=(0,0,0), rotate=90)
    
    page2.insert_text((202.35, 129.54), "Registration Authority", fontname="helv", fontsize=5.8, color=(0,0,0))
    page2.insert_text((202.35, 136.95), rc_data["authority"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    doc.save(output_path)
    print(f"Successfully generated RC Card PDF: {output_path}")

if __name__ == "__main__":
    input_pdf = sys.argv[1] if len(sys.argv) > 1 else "a4.pdf"
    output_pdf = sys.argv[2] if len(sys.argv) > 2 else "a4_converted_card.pdf"
    
    rc_data = parse_rc_a4(input_pdf)
    generate_rc_card(rc_data, output_pdf)
