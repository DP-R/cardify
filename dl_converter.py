#!/usr/bin/env python3
"""
DL Card Converter: Extracts Driving Licence data from dl_a4.pdf
and formats it into the card format of dl_card.pdf.
"""

import sys
import os
import re
import fitz  # PyMuPDF

def parse_dl_a4(pdf_path="dl_a4.pdf"):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Input PDF file not found: {pdf_path}")

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
            if (base_img["ext"] in ["jpeg", "jpg"] or base_img["width"] == 215) and len(base_img["image"]) > 2000:
                with open(photo_path, "wb") as f:
                    f.write(base_img["image"])
            elif base_img["width"] == 200 and base_img["height"] == 200 and len(base_img["image"]) > 1000:
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
                    
    data["photo_path"] = photo_path
    data["qr_path"] = qr_path
    return data


def generate_dl_card(dl_data, output_path="dl_a4_converted_card.pdf"):
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
        
    # Vertical Date Of First Issue (rotate=90)
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
    print(f"Successfully generated DL Card PDF: {output_path}")

if __name__ == "__main__":
    input_pdf = sys.argv[1] if len(sys.argv) > 1 else "dl_a4.pdf"
    output_pdf = sys.argv[2] if len(sys.argv) > 2 else "dl_a4_converted_card.pdf"
    
    dl_data = parse_dl_a4(input_pdf)
    generate_dl_card(dl_data, output_pdf)
