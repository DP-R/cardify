import fitz
import os
import re

from generate_final_cards import parse_rc_a4

def create_perfect_rc_card(rc_data, output_path="a4_converted_card.pdf"):
    doc = fitz.open()
    
    # ==================== PAGE 1 (Front) ====================
    page1 = doc.new_page(width=612.0, height=792.0)
    
    # 1. Background image
    bg1_rect = fitz.Rect(0.0, 0.0, 260.34677, 162.87095)
    page1.insert_image(bg1_rect, filename="rc_card_tmpl_p1_img_1.png")
    
    # 2. NT & AP Circle Badges Top-Right
    # NT circle: center=(229.67, 16.04), r=6.48, color=(68/255, 199/255, 241/255)
    nt_center = fitz.Point(229.67, 16.04)
    page1.draw_circle(nt_center, 6.48, color=(0,0,0), fill=(68/255, 199/255, 241/255), width=0.5)
    page1.insert_text((226.2, 18.0), "NT", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    # AP circle: center=(245.09, 16.04), r=6.48, color=(248/255, 149/255, 29/255)
    ap_center = fitz.Point(245.09, 16.04)
    page1.draw_circle(ap_center, 6.48, color=(0,0,0), fill=(248/255, 149/255, 29/255), width=0.5)
    page1.insert_text((241.6, 18.0), "AP", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    # 3. Headers
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
    
    # Address wrapping within card right boundary (x <= 238pt)
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
        
    # Fuel & Emission Norms
    page1.insert_text((7.40, 128.31), "Fuel", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((7.40, 135.11), rc_data["fuel"], fontname="helv", fontsize=5.8, color=(0,0,0))
    page1.insert_text((7.40, 142.51), "Emission Norms", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page1.insert_text((7.40, 149.91), "BHARAT STAGE", fontname="helv", fontsize=5.8, color=(0,0,0))
    page1.insert_text((7.40, 156.71), "VI", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    # Vertical Card Issue Date (reading from bottom to top, rotate=90)
    card_issue_str = f"Card Issue Date ({rc_data['tx_date']})"
    page1.insert_text((253.50, 140.40), card_issue_str, fontname="helv", fontsize=5.8, color=(0,0,0), rotate=90)
    
    # ==================== PAGE 2 (Back) ====================
    page2 = doc.new_page(width=612.0, height=792.0)
    
    # 1. Background image
    bg2_rect = fitz.Rect(0.0, 0.0, 260.34677, 162.87095)
    page2.insert_image(bg2_rect, filename="rc_card_tmpl_p2_img_1.png")
    
    # 2. NT & AP Circle Badges Top-Left
    nt_center_p2 = fitz.Point(14.19, 16.04)
    page2.draw_circle(nt_center_p2, 6.48, color=(0,0,0), fill=(68/255, 199/255, 241/255), width=0.5)
    page2.insert_text((10.7, 18.0), "NT", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    ap_center_p2 = fitz.Point(29.61, 16.04)
    page2.draw_circle(ap_center_p2, 6.48, color=(0,0,0), fill=(248/255, 149/255, 29/255), width=0.5)
    page2.insert_text((26.1, 18.0), "AP", fontname="helv", fontsize=5.8, color=(0,0,0))
    
    # 3. QR Code (exact 67.86pt x 67.86pt box)
    qr_rect = fitz.Rect(7.403, 43.185, 75.266, 111.048)
    if os.path.exists(rc_data["qr_path"]):
        page2.insert_image(qr_rect, filename=rc_data["qr_path"])
        
    # Left column below QR code
    page2.insert_text((7.40, 35.20), "Regn. Number", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((7.40, 42.60), rc_data["reg_no"], fontname="hebo", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((7.40, 120.30), "Month-Year of Mfg.", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((7.40, 127.10), rc_data["mfg_date"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    page2.insert_text((7.40, 134.50), "No. of Cylinders  ", fontname="hebo", fontsize=5.8, color=(0,0,0))
    page2.insert_text((54.74, 134.50), rc_data["cylinders"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    # Vehicle Class: "Vehicle Class: " is BOLD, value is REGULAR!
    page2.insert_text((80.62, 17.30), "Vehicle Class: ", fontname="hebo", fontsize=5.8, color=(0,0,0))
    v_class_str = "M-CYCLE/SCOOTER (2WN)" if "MOTOR CYCLE" in rc_data["vehicle_class"].upper() else rc_data["vehicle_class"]
    page2.insert_text((120.94, 17.30), v_class_str, fontname="helv", fontsize=5.8, color=(0,0,0))
    
    # Main Body Details
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
    
    # Vertical Form 23A on right edge (rotate=90)
    page2.insert_text((253.33, 107.54), "Form 23A", fontname="helv", fontsize=5.8, color=(0,0,0), rotate=90)
    
    # Registration Authority
    page2.insert_text((188.00, 129.54), "Registration Authority", fontname="helv", fontsize=5.8, color=(0,0,0))
    page2.insert_text((195.00, 136.95), rc_data["authority"], fontname="helv", fontsize=5.8, color=(0,0,0))
    
    doc.save(output_path)
    print(f"Successfully generated perfect RC card: {output_path}")

if __name__ == "__main__":
    rc_data = parse_rc_a4("a4.pdf")
    create_perfect_rc_card(rc_data, "a4_converted_card.pdf")
    create_perfect_rc_card(rc_data, "card_converted.pdf")
