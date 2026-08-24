import fitz
import os
import re

def parse_rc_a4(pdf_path="a4.pdf"):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Input PDF file not found: {pdf_path}")
        
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
        
    def get_field(label, next_label=None, default=""):
        # 1. Try colon format: "Label : Value"
        m = re.search(fr"{label}\s*:\s*([^\n]+)", text)
        if m:
            return m.group(1).strip()
            
        # 2. Try newline format
        if next_label:
            m = re.search(fr"{label}\s*\n(.*?)\s*(?:{next_label})", text, re.DOTALL)
            if m:
                val = m.group(1).strip()
                val = re.sub(r'\s+', ' ', val)
                return val
        else:
            m = re.search(fr"{label}\s*\n([^\n]+)", text)
            if m:
                return m.group(1).strip()
                
        return default

    data = {}
    data["reg_no"] = get_field("Registration Number", "Registered Owner", "")
    data["owner_name"] = get_field("Registered Owner", r"D/o or S/o or W/o or", "")
    data["swd_of"] = get_field(r"D/o or S/o or W/o or\s*\n*Rep", "Present Address")
    if not data["swd_of"]:
        data["swd_of"] = get_field(r"D/o or S/o or W/o or\s*Rep", None, "")
        
    data["address"] = get_field("Present Address", "Date Of Registration", "")
    data["reg_date"] = get_field("Date Of Registration", r"VEHICLE DETAILED DESCRIPTION|Vehicle Class", "")
    
    data["vehicle_class"] = get_field("Vehicle Class", "Makers Name", "")
    data["maker_name"] = get_field("Makers Name", "Body Type", "")
    data["body_type"] = get_field("Body Type", r"Mth\.Yr\.of Mfg", "")
    
    mfg = get_field(r"Mth\.Yr\.of Mfg\(mmyyyy\)", r"No\. of Cylinder")
    if mfg and len(mfg.replace(" ","")) == 6:
        mfg = mfg.replace(" ","")
        data["mfg_date"] = f"{mfg[:2]}-{mfg[2:]}"
    else:
        data["mfg_date"] = mfg if mfg else ""
        
    data["cylinders"] = get_field(r"No\. of Cylinder", "Chassis Number", "")
    data["chassis_no"] = get_field("Chassis Number", "Engine Number", "")
    data["engine_no"] = get_field("Engine Number", "Fuel Used", "")
    data["fuel"] = get_field("Fuel Used", "Engine Power", "")
    data["hp"] = get_field("Engine Power", "Cubic Capacity", "")
    data["cc"] = get_field("Cubic Capacity", r"Maker's", "")
    
    data["model_name"] = get_field(r"Maker's\s*\n*Classification", "Wheel Base")
    if not data["model_name"]:
        data["model_name"] = get_field(r"Maker's Classification", None, "")
        
    data["wheelbase"] = get_field("Wheel Base", "Seating Capacity", "")
    data["seating"] = get_field("Seating Capacity", "Unladen Weight", "")
    
    unladen = get_field("Unladen Weight", "Colour")
    data["unladen_wt"] = unladen.replace("Kgs", "").replace("kgs", "").strip() if unladen else ""
    
    data["colour"] = get_field("Colour", "GVW", "")
    
    gvw = get_field("GVW", r"VEHICLE TYRE|Registration Valid")
    if not gvw:
        gvw = get_field("GVW", None)
    data["laden_wt"] = gvw.replace("Kgs", "").replace("kgs", "").strip() if gvw else ""
    
    data["valid_upto"] = get_field("Registration Valid Upto", "Registering Authority", "")
    
    auth = get_field("Registering Authority", "Owner Type", "")
    if "Description" in auth or "Weights" in auth:
        auth = re.sub(r'Description.*?Weights\s*', '', auth).strip()
    data["authority"] = auth
    
    data["owner_type"] = get_field("Owner Type", "Invoice Amount", "")
    
    tx = get_field("Transaction Date", "Visit Url", "")
    if tx and tx.startswith(":"):
        tx = tx[1:].strip()
    data["tx_date"] = tx

    # Extract QR Code
    qr_path = "extracted_rc_qr.png"
    for page in doc:
        for img_info in page.get_images():
            xref = img_info[0]
            base_img = doc.extract_image(xref)
            if base_img["width"] == 200 and base_img["height"] == 200 and len(base_img["image"]) > 1000:
                try:
                    import io
                    from PIL import Image, ImageChops
                    im = Image.open(io.BytesIO(base_img["image"]))
                    bg = Image.new(im.mode, im.size, (255,255,255))
                    diff = ImageChops.difference(im, bg)
                    bbox = diff.getbbox()
                    if bbox:
                        im = im.crop(bbox)
                    im.save(qr_path)
                except Exception:
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
    data["dl_no"] = m.group(1).strip() if m else ""
    
    m = re.search(r"Name\s*:\s*(.+)", text)
    data["name"] = m.group(1).strip() if m else ""
    
    m = re.search(r"Son/Wife/Daughter of\s*:\s*(.+)", text)
    data["swd_of"] = m.group(1).strip() if m else ""
    
    m = re.search(r"Date of Birth\s*:\s*(.+)", text)
    data["dob"] = m.group(1).strip() if m else ""
    
    m = re.search(r"Present Address\s*:\s*([\s\S]+?)(?=Issue Date|Date of Validity|NATIONALITY)", text)
    if m:
        addr = m.group(1).replace("\n", " ").strip()
        addr = re.sub(r"\s+", " ", addr)
        data["address"] = addr
    else:
        data["address"] = ""
        
    m = re.search(r"Issue Date\s*:\s*(.+)", text)
    data["issue_date"] = m.group(1).strip() if m else ""
    
    m = re.search(r"Date of Validity\s*:\s*(.+)", text)
    data["validity_nt"] = m.group(1).strip() if m else ""
    
    m = re.search(r"Date of first Issue\s*:\s*(.+)", text)
    data["first_issue"] = m.group(1).strip() if m else ""
    
    m = re.search(r"Orginal LA\.\s*:\s*(.+)", text)
    data["original_la"] = m.group(1).strip() if m else ""
    
    m = re.search(r"Blood Group\s*:\s*(.*)", text)
    data["blood_group"] = m.group(1).strip() if m else ""
    
    data["authority"] = ""
    
    photo_path = "extracted_dl_photo.jpeg"
    qr_path = "extracted_dl_qr.png"
    
    for page in doc:
        for img_info in page.get_images():
            xref = img_info[0]
            base_img = doc.extract_image(xref)
            if base_img["ext"] in ["jpeg", "jpg"] or base_img["width"] == 215:
                with open(photo_path, "wb") as f:
                    f.write(base_img["image"])
            elif base_img["width"] == 200 and base_img["height"] == 200:
                with open(qr_path, "wb") as f:
                    f.write(base_img["image"])
                    
    data["photo_path"] = photo_path
    data["qr_path"] = qr_path
    return data


def create_rc_card_pdf(rc_data, output_path):
    doc = fitz.open()
    
    # ---------------- PAGE 1 (Front) ----------------
    page1 = doc.new_page(width=612.0, height=792.0)
    bg1_rect = fitz.Rect(0.0, 0.0, 260.34677, 162.87095)
    page1.insert_image(bg1_rect, filename="rc_card_tmpl_p1_img_1.png")
    
    # Header
    page1.insert_text((55.52, 13.75), "Indian Union Vehicle Registration Certificate", fontname="hebo", fontsize=6.6, color=(0,0,0))
    page1.insert_text((55.52, 21.75), "Issued by Government of Andhra Pradesh", fontname="hebo", fontsize=6.6, color=(0,0,0))
    page1.insert_text((223.20, 19.11), "NT  AP", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    # Grid Row 1
    page1.insert_text((59.64, 40.71), "Regn No", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((59.64, 48.11), rc_data["reg_no"], fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    page1.insert_text((106.84, 40.71), "Date of Regn.", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((106.84, 48.11), rc_data["reg_date"], fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    page1.insert_text((154.03, 40.71), "Regn. Validity", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((154.03, 48.11), rc_data["valid_upto"], fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    page1.insert_text((201.23, 40.71), "Owner", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((201.23, 48.11), "Serial", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((227.99, 45.02), "1", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    # Main fields
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
    
    addr = rc_data["address"]
    if len(addr) > 55:
        idx = addr.rfind(",", 0, 55)
        if idx == -1: idx = addr.rfind(" ", 0, 55)
        if idx == -1: idx = 55
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
    
    card_issue_str = f"Card Issue Date ({rc_data['tx_date']})"
    page1.insert_text((247.07, 140.40), card_issue_str, fontname="helv", fontsize=5.8, color=(0,0,0), rotate=270)
    
    # ---------------- PAGE 2 (Back) ----------------
    page2 = doc.new_page(width=612.0, height=792.0)
    bg2_rect = fitz.Rect(0.0, 0.0, 260.34677, 162.87095)
    page2.insert_image(bg2_rect, filename="rc_card_tmpl_p2_img_1.png")
    
    qr_rect = fitz.Rect(7.403, 43.185, 75.266, 111.048)
    if os.path.exists(rc_data["qr_path"]):
        page2.insert_image(qr_rect, filename=rc_data["qr_path"])
        
    page2.insert_text((10.35, 19.11), "NT  AP", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((7.40, 35.20), "Regn. Number", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((7.40, 42.60), rc_data["reg_no"], fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((7.40, 120.30), "Month-Year of Mfg.", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((7.40, 127.10), rc_data["mfg_date"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((7.40, 134.50), f"No. of Cylinders  {rc_data['cylinders']}", fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    v_class_str = "M-CYCLE/SCOOTER (2WN)" if "MOTOR CYCLE" in rc_data["vehicle_class"].upper() else rc_data["vehicle_class"]
    page2.insert_text((80.62, 17.30), f"Vehicle Class: {v_class_str}", fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((80.62, 35.20), "Maker's Name:", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((80.62, 42.60), rc_data["maker_name"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((80.62, 50.60), "Model Name:", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((80.62, 58.00), rc_data["model_name"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((80.62, 65.40), "Colour:", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((154.60, 65.40), "/ Body Type:", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((80.62, 72.20), rc_data["colour"], fontname="helv", fontsize=5.8, color=(0,0,0))
    page2.insert_text((154.60, 72.20), f"/ {rc_data['body_type']}", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((80.62, 79.60), "Seating(in all) Capacity", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((80.62, 87.00), rc_data["seating"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((80.62, 93.80), "Unladen/ Laden Weight (Kg)", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((80.62, 101.20), f"{rc_data['unladen_wt']} / {rc_data['laden_wt']}", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((80.62, 108.60), "Cubic Cap./ Horse Power (BHP/Kw)", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((80.62, 115.40), f"{rc_data['cc']} / {rc_data['hp']}", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((179.28, 108.60), "/ Wheel Base(mm)", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((179.28, 115.40), f"/ {rc_data['wheelbase']}", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((246.90, 107.54), "Form 23A", fontname="helv", fontsize=5.8, color=(0,0,0), rotate=270)
    
    page2.insert_textbox(fitz.Rect(180.0, 124.0, 255.0, 133.0), "Registration Authority", fontname="helv", fontsize=5.8, color=(0,0,0), align=fitz.TEXT_ALIGN_RIGHT)
    page2.insert_textbox(fitz.Rect(180.0, 133.0, 255.0, 148.0), rc_data["authority"], fontname="helv", fontsize=5.8, color=(0,0,0), align=fitz.TEXT_ALIGN_RIGHT)
    
    doc.save(output_path)
    print(f"Saved RC Card to {output_path}")


def create_dl_card_pdf(dl_data, output_path):
    doc = fitz.open()
    
    # ---------------- PAGE 1 (Front) ----------------
    page1 = doc.new_page(width=241.0, height=153.0)
    bg1_rect = fitz.Rect(0.0, 0.0, 241.0, 153.0)
    page1.insert_image(bg1_rect, filename="dl_card_tmpl_p1_img_3.jpeg")
    
    photo_rect = fitz.Rect(185.0, 33.0, 225.0, 83.0)
    if os.path.exists(dl_data["photo_path"]):
        page1.insert_image(photo_rect, filename=dl_data["photo_path"])
        
    aadhaar_rect = fitz.Rect(180.0, 85.0, 235.0, 100.0)
    if os.path.exists("dl_card_tmpl_p1_img_2.jpeg"):
        page1.insert_image(aadhaar_rect, filename="dl_card_tmpl_p1_img_2.jpeg")
        
    page1.insert_text((9.42, 18.42), "Indian Union Driving Licence", fontname="hebo", fontsize=9.0, color=(0,0,0))
    page1.insert_text((22.73, 29.73), "Issued by ANDHRA PRADESH", fontname="hebo", fontsize=7.0, color=(0,0,0))
    page1.insert_text((218.0, 19.0), "AP", fontname="hebo", fontsize=7.0, color=(0,0,0))
    
    page1.insert_text((36.73, 43.73), dl_data["dl_no"], fontname="hebo", fontsize=7.0, color=(0,0,0))
    
    page1.insert_text((49.62, 55.62), " Issue Date    Validity ( NT )   Validity  ( TR )", fontname="hebo", fontsize=6.0, color=(0,0,0))
    page1.insert_text((59.62, 65.62), f"{dl_data['issue_date']}        {dl_data['validity_nt']}             NA", fontname="hebo", fontsize=6.0, color=(0,0,0))
    
    page1.insert_text((82.62, 88.62), f"Name : {dl_data['name']}", fontname="hebo", fontsize=6.0, color=(0,0,0))
    
    dob_str = f"Date Of Birth : {dl_data['dob']}  Blood Group: {dl_data['blood_group']}"
    page1.insert_text((97.12, 103.12), dob_str, fontname="hebo", fontsize=6.0, color=(0,0,0))
    page1.insert_text((96.62, 102.62), "Organ Donor: No", fontname="hebo", fontsize=6.0, color=(0,0,0))
    
    page1.insert_text((105.62, 111.62), f"Son/Daughter/Wife of : {dl_data['swd_of']}", fontname="hebo", fontsize=6.0, color=(0,0,0))
    
    page1.insert_text((117.62, 123.62), "Address:", fontname="hebo", fontsize=6.0, color=(0,0,0))
    
    addr = dl_data["address"]
    lines = []
    curr = ""
    for token in addr.split():
        if len(curr) + len(token) + 1 <= 35:
            curr += (" " if curr else "") + token
        else:
            lines.append(curr)
            curr = token
    if curr: lines.append(curr)
    
    y_off = 129.0
    for l in lines[:3]:
        page1.insert_text((123.0, y_off), l, fontname="hebo", fontsize=6.0, color=(0,0,0))
        y_off += 6.5
        
    first_issue_str = f"Date Of First Issue  {dl_data['first_issue']}"
    page1.insert_text((235.0, 129.0), first_issue_str, fontname="hebo", fontsize=6.0, color=(0,0,0), rotate=270)
    
    # ---------------- PAGE 2 (Back) ----------------
    page2 = doc.new_page(width=241.0, height=153.0)
    bg2_rect = fitz.Rect(0.0, 0.0, 241.0, 153.0)
    page2.insert_image(bg2_rect, filename="dl_card_tmpl_p2_img_4.jpeg")
    
    page2.insert_text((10.12, 16.12), f"DL No: {dl_data['dl_no']}", fontname="hebo", fontsize=6.0, color=(0,0,0))
    
    qr_rect = fitz.Rect(8.0, 20.0, 44.0, 56.0)
    if os.path.exists(dl_data["qr_path"]):
        page2.insert_image(qr_rect, filename=dl_data["qr_path"])
        
    page2.insert_text((28.12, 34.12), "ADPVEH No.(Regn.Numbers)", fontname="hebo", fontsize=6.0, color=(0,0,0))
    page2.insert_text((46.12, 52.12), "Hazardous validity        Hill Validity", fontname="hebo", fontsize=6.0, color=(0,0,0))
    
    page2.insert_text((67.14, 72.14), "Class of", fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((72.89, 77.89), "Vehicle", fontname="hebo", fontsize=5.0, color=(0,0,0))
    
    page2.insert_text((70.02, 75.02), "Code", fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((70.02, 75.02), "Issued by", fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((68.14, 73.14), "Date of", fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((73.89, 78.89), "Issue", fontname="hebo", fontsize=5.0, color=(0,0,0))
    
    page2.insert_text((67.64, 72.64), "Vehicle Category", fontname="hebo", fontsize=5.0, color=(0,0,0))
    
    bike_rect = fitz.Rect(8.0, 80.0, 28.0, 92.0)
    if os.path.exists("dl_card_tmpl_p2_img_1.jpeg"):
        page2.insert_image(bike_rect, filename="dl_card_tmpl_p2_img_1.jpeg")
        
    page2.insert_text((38.0, 88.0), "MCWG", fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((65.0, 88.0), dl_data["original_la"], fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((90.0, 88.0), dl_data["issue_date"], fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((125.0, 88.0), "NT", fontname="hebo", fontsize=5.0, color=(0,0,0))
    
    page2.insert_text((38.0, 98.0), "LMV", fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((65.0, 98.0), dl_data["original_la"], fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((90.0, 98.0), dl_data["issue_date"], fontname="hebo", fontsize=5.0, color=(0,0,0))
    page2.insert_text((125.0, 98.0), "NT", fontname="hebo", fontsize=5.0, color=(0,0,0))
    
    auth_badge_rect = fitz.Rect(158.0, 126.0, 235.0, 148.0)
    if os.path.exists("dl_card_tmpl_p2_img_3.jpeg"):
        page2.insert_image(auth_badge_rect, filename="dl_card_tmpl_p2_img_3.jpeg")
        
    page2.insert_text((10.0, 146.0), "Emergency Contact Number\n91-", fontname="helv", fontsize=5.0, color=(0,0,0))
    
    page2.insert_text((236.0, 90.0), "Form 7 Rule 16(2)", fontname="hebo", fontsize=5.0, color=(0,0,0), rotate=270)
    
    doc.save(output_path)
    print(f"Saved DL Card to {output_path}")

if __name__ == "__main__":
    rc_data = parse_rc_a4("a4.pdf")
    create_rc_card_pdf(rc_data, "a4_converted_card.pdf")
    create_rc_card_pdf(rc_data, "card_converted.pdf")

    dl_data = parse_dl_a4("dl_a4.pdf")
    create_dl_card_pdf(dl_data, "dl_a4_converted_card.pdf")
    create_dl_card_pdf(dl_data, "dl_card_converted.pdf")
