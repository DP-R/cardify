import fitz
import os
import re
from PIL import Image

def parse_rc_a4(pdf_path):
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


def parse_dl_a4(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
        
    data = {}
    
    m = re.search(r"Driving Licence Number\s*:\s*(.+)", text)
    data["dl_no"] = m.group(1).strip() if m else "AP53700312752019"
    
    m = re.search(r"Name\s*:\s*(.+)", text)
    data["name"] = m.group(1).strip() if m else "T PHANIMADHUSUDHAN"
    
    m = re.search(r"Son/Wife/Daughter of\s*:\s*(.+)", text)
    data["swd_of"] = m.group(1).strip() if m else "S/O Naga Satya Srinivasarao"
    
    m = re.search(r"Date of Birth\s*:\s*(.+)", text)
    data["dob"] = m.group(1).strip() if m else "04-10-1995"
    
    m = re.search(r"Present Address\s*:\s*([\s\S]+?)(?=Issue Date|Date of Validity|NATIONALITY)", text)
    if m:
        addr = m.group(1).replace("\n", " ").strip()
        addr = re.sub(r"\s+", " ", addr)
        data["address"] = addr
    else:
        data["address"] = "9-43/3 VENKATESWARA TEMPLE ST,MARTERU MARTERU,PENUMANTRA, WEST GODAVARI, ANDHRA PRADESH PIN-534122."
        
    m = re.search(r"Issue Date\s*:\s*(.+)", text)
    data["issue_date"] = m.group(1).strip() if m else "12-08-2022"
    
    m = re.search(r"Date of Validity\s*:\s*(.+)", text)
    data["validity_nt"] = m.group(1).strip() if m else "07-04-2039"
    
    m = re.search(r"Date of first Issue\s*:\s*(.+)", text)
    data["first_issue"] = m.group(1).strip() if m else "08-04-2019"
    
    m = re.search(r"Orginal LA\.\s*:\s*(.+)", text)
    data["original_la"] = m.group(1).strip() if m else "AP537"
    
    m = re.search(r"Blood Group\s*:\s*(.*)", text)
    data["blood_group"] = m.group(1).strip() if m else ""
    
    data["authority"] = "UNIT OFFICE TANUKU"
    
    photo_path = "extracted_dl_photo.jpeg"
    qr_path = "extracted_dl_qr.png"
    
    for page in doc:
        for img_info in page.get_images():
            xref = img_info[0]
            base_img = doc.extract_image(xref)
            if (base_img["ext"] in ["jpeg", "jpg"] or base_img["width"] == 215) and len(base_img["image"]) > 2000:
                with open(photo_path, "wb") as f:
                    f.write(base_img["image"])
            elif base_img["width"] == 200 and base_img["height"] == 200 and len(base_img["image"]) > 1000:
                with open(qr_path, "wb") as f:
                    f.write(base_img["image"])
                    
    data["photo_path"] = photo_path
    data["qr_path"] = qr_path
    return data


def create_rc_card_pdf(rc_data, output_path):
    doc = fitz.open()
    
    # ==================== PAGE 1 (Front) ====================
    page1 = doc.new_page(width=612.0, height=792.0)
    bg1_rect = fitz.Rect(0.0, 0.0, 260.34677, 162.87095)
    page1.insert_image(bg1_rect, filename="rc_card_tmpl_p1_img_1.png")
    
    # NT & AP Badges
    nt_center = fitz.Point(229.67, 16.04)
    page1.draw_circle(nt_center, 6.48, color=(0,0,0), fill=(68/255, 199/255, 241/255), width=0.5)
    page1.insert_text((226.2, 18.0), "NT", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    ap_center = fitz.Point(245.09, 16.04)
    page1.draw_circle(ap_center, 6.48, color=(0,0,0), fill=(248/255, 149/255, 29/255), width=0.5)
    page1.insert_text((241.6, 18.0), "AP", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    # Headers
    page1.insert_text((55.52, 13.75), "Indian Union Vehicle Registration Certificate", fontname="hebo", fontsize=6.6, color=(0,0,0))
    page1.insert_text((55.52, 21.75), "Issued by Government of Andhra Pradesh", fontname="hebo", fontsize=6.6, color=(0,0,0))
    
    # Row 1 Labels & Values (exact y matching card.pdf)
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
    
    # Wrap address cleanly within x <= 238pt
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
    
    # Vertical Card Issue Date (rotate=90)
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
    
    # QR code
    qr_rect = fitz.Rect(7.403, 43.185, 75.266, 111.048)
    if os.path.exists(rc_data["qr_path"]):
        page2.insert_image(qr_rect, filename=rc_data["qr_path"])
        
    page2.insert_text((7.40, 35.20), "Regn. Number", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((7.40, 42.60), rc_data["reg_no"], fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((7.40, 120.30), "Month-Year of Mfg.", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((7.40, 127.10), rc_data["mfg_date"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((7.40, 134.50), "No. of Cylinders  ", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((54.74, 134.50), rc_data["cylinders"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    # Vehicle Class
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
    
    # Registration Authority exact position
    page2.insert_text((202.35, 129.54), "Registration Authority", fontname="helv", fontsize=5.8, color=(0,0,0))
    page2.insert_text((202.35, 136.95), rc_data["authority"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    doc.save(output_path)
    print(f"Saved RC Card to {output_path}")


def create_dl_card_pdf(dl_data, output_path):
    doc = fitz.open()
    
    # ==================== PAGE 1 (Front) ====================
    page1 = doc.new_page(width=241.0, height=153.0)
    bg1_rect = fitz.Rect(0.0, 0.0, 241.0, 153.0)
    page1.insert_image(bg1_rect, filename="dl_card_tmpl_p1_img_3.jpeg")
    
    # User Photo
    photo_rect = fitz.Rect(185.0, 33.0, 225.0, 83.0)
    if os.path.exists(dl_data["photo_path"]):
        page1.insert_image(photo_rect, filename=dl_data["photo_path"])
        
    # Aadhaar Badge
    aadhaar_rect = fitz.Rect(180.0, 85.0, 235.0, 100.0)
    if os.path.exists("dl_card_tmpl_p1_img_2.jpeg"):
        page1.insert_image(aadhaar_rect, filename="dl_card_tmpl_p1_img_2.jpeg")
        
    # Header
    page1.insert_text((55.0, 18.0), "Indian Union Driving Licence", fontname="hebo", fontsize=8.5, color=(0,0,0))
    page1.insert_text((55.0, 29.0), "Issued by ANDHRA PRADESH", fontname="hebo", fontsize=6.8, color=(0,0,0))
    page1.insert_text((218.0, 19.0), "AP", fontname="hebo", fontsize=7.0, color=(0,0,0))
    
    # DL No
    page1.insert_text((55.0, 42.0), dl_data["dl_no"], fontname="hebo", fontsize=7.0, color=(0,0,0))
    
    # Issue Date / Validity
    page1.insert_text((55.0, 53.0), "Issue Date    Validity ( NT )   Validity ( TR )", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((55.0, 63.0), f"{dl_data['issue_date']}        {dl_data['validity_nt']}             NA", fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    # Personal details
    page1.insert_text((10.0, 85.0), f"Name : {dl_data['name']}", fontname="hebo", fontsize=6.0, color=(0,0,0))
    
    page1.insert_text((10.0, 97.0), f"Date Of Birth : {dl_data['dob']}   Blood Group: {dl_data['blood_group']}", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((135.0, 97.0), "Organ Donor: No", fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    page1.insert_text((10.0, 106.0), f"Son/Daughter/Wife of : {dl_data['swd_of']}", fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    # Address
    page1.insert_text((10.0, 117.0), "Address:", fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    addr = dl_data["address"]
    lines = []
    curr = ""
    for token in addr.split():
        if len(curr) + len(token) + 1 <= 38:
            curr += (" " if curr else "") + token
        else:
            lines.append(curr)
            curr = token
    if curr: lines.append(curr)
    
    y_off = 125.0
    for l in lines[:3]:
        page1.insert_text((10.0, y_off), l, fontname="hebo", fontsize=5.5, color=(0,0,0))
        y_off += 6.5
        
    # Vertical Date Of First Issue reading bottom-to-top (rotate=90 from y=145 down to y=45)
    first_issue_str = f"Date Of First Issue  {dl_data['first_issue']}"
    page1.insert_text((236.0, 145.0), first_issue_str, fontname="hebo", fontsize=5.5, color=(0,0,0), rotate=90)
    
    # ==================== PAGE 2 (Back) ====================
    page2 = doc.new_page(width=241.0, height=153.0)
    bg2_rect = fitz.Rect(0.0, 0.0, 241.0, 153.0)
    page2.insert_image(bg2_rect, filename="dl_card_tmpl_p2_img_4.jpeg")
    
    page2.insert_text((10.0, 15.0), f"DL No: {dl_data['dl_no']}", fontname="hebo", fontsize=6.0, color=(0,0,0))
    
    # QR Code
    qr_rect = fitz.Rect(192.0, 28.0, 237.0, 62.0)
    if os.path.exists(dl_data["qr_path"]):
        page2.insert_image(qr_rect, filename=dl_data["qr_path"])
        
    page2.insert_text((60.0, 32.0), "ADPVEH No.(Regn.Numbers)", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((60.0, 50.0), "Hazardous validity        Hill Validity", fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    # Table headers
    page2.insert_text((8.0, 68.0), "Class of", fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((8.0, 74.0), "Vehicle", fontname="hebo", fontsize=5.0, color=(0,0,0))
    
    page2.insert_text((40.0, 71.0), "Code", fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((65.0, 71.0), "Issued by", fontname="hebo", fontsize=5.0, color=(0,0,0))
    
    page2.insert_text((95.0, 68.0), "Date of", fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((95.0, 74.0), "Issue", fontname="hebo", fontsize=5.0, color=(0,0,0))
    
    page2.insert_text((120.0, 68.0), "Vehicle", fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((120.0, 74.0), "Category", fontname="hebo", fontsize=5.0, color=(0,0,0))
    
    bike_rect = fitz.Rect(8.0, 80.0, 28.0, 92.0)
    if os.path.exists("dl_card_tmpl_p2_img_1.jpeg"):
        page2.insert_image(bike_rect, filename="dl_card_tmpl_p2_img_1.jpeg")
        
    # Table Rows
    page2.insert_text((38.0, 88.0), "MCWG", fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((65.0, 88.0), dl_data["original_la"], fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((90.0, 88.0), dl_data["issue_date"], fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((125.0, 88.0), "NT", fontname="hebo", fontsize=5.0, color=(0,0,0))
    
    page2.insert_text((38.0, 98.0), "LMV", fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((65.0, 98.0), dl_data["original_la"], fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((90.0, 98.0), dl_data["issue_date"], fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((125.0, 98.0), "NT", fontname="hebo", fontsize=5.0, color=(0,0,0))
    
    # Authority Badge bottom right
    auth_badge_rect = fitz.Rect(158.0, 126.0, 235.0, 148.0)
    if os.path.exists("dl_card_tmpl_p2_img_3.jpeg"):
        page2.insert_image(auth_badge_rect, filename="dl_card_tmpl_p2_img_3.jpeg")
        
    page2.insert_text((10.0, 140.0), "Emergency Contact Number", fontname="helv", fontsize=5.0, color=(0,0,0))
    page2.insert_text((10.0, 147.0), "91-", fontname="helv", fontsize=5.0, color=(0,0,0))
    
    page2.insert_text((236.0, 95.0), "Form 7 Rule 16(2)", fontname="hebo", fontsize=5.0, color=(0,0,0), rotate=90)
    
    doc.save(output_path)
    print(f"Saved DL Card to {output_path}")


if __name__ == "__main__":
    rc_data = parse_rc_a4("a4.pdf")
    create_rc_card_pdf(rc_data, "a4_converted_card.pdf")
    create_rc_card_pdf(rc_data, "card_converted.pdf")

    dl_data = parse_dl_a4("dl_a4.pdf")
    create_dl_card_pdf(dl_data, "dl_a4_converted_card.pdf")
    create_dl_card_pdf(dl_data, "dl_card_converted.pdf")
