import fitz
import os
import re

from generate_all_cards import parse_rc_a4, parse_dl_a4

def convert_rc_card(rc_data, template_pdf="card.pdf", output_pdf="a4_converted_card.pdf"):
    doc = fitz.open(template_pdf)
    
    # ------------ PAGE 1 (Front) ------------
    page1 = doc[0]
    
    # 1. Map of old text -> new text
    p1_replacements = [
        ("AP39FE5474", rc_data["reg_no"], "hebo", 5.8),
        ("24-Jul-2020", rc_data["reg_date"], "hebo", 5.8),
        ("23-Jul-2035", rc_data["valid_upto"], "hebo", 5.8),
        ("MB8DP12DAL8112956", rc_data["chassis_no"], "helv", 5.8),
        ("AF212262873", rc_data["engine_no"], "helv", 5.8),
        ("APPARI BHAVESH", rc_data["owner_name"], "helv", 5.8),
        ("APPARI PRASAD", rc_data["swd_of"], "helv", 5.8),
    ]
    
    # Handle address
    addr_instances = page1.search_for("7-21,KOTHAPALEM, MACHAVARAM, , KONASEEMA-ANDHRA PRADESH-")
    addr_533_instances = page1.search_for("533214")
    
    # Collect search rects first
    p1_actions = []
    for old_txt, new_txt, font, sz in p1_replacements:
        rects = page1.search_for(old_txt)
        for r in rects:
            p1_actions.append((r, old_txt, new_txt, font, sz))
            
    # Redact address
    for r in addr_instances + addr_533_instances:
        page1.add_redact_annot(r, fill=None)
        
    for r, old_txt, new_txt, font, sz in p1_actions:
        page1.add_redact_annot(r, fill=None)
        
    # Card issue date
    issue_date_rects = page1.search_for("18-Jul-2026")
    for r in issue_date_rects:
        page1.add_redact_annot(r, fill=None)
        
    page1.apply_redactions()
    
    # Re-insert new values
    for r, old_txt, new_txt, font, sz in p1_actions:
        page1.insert_text((r.x0, r.y1), new_txt, fontname=font, fontsize=sz, color=(0,0,0))
        
    # Re-insert address
    if addr_instances:
        r_addr = addr_instances[0]
        addr = rc_data["address"]
        if len(addr) > 55:
            idx = addr.rfind(",", 0, 55)
            if idx == -1: idx = addr.rfind(" ", 0, 55)
            if idx == -1: idx = 55
            l1 = addr[:idx+1].strip()
            l2 = addr[idx+1:].strip()
            page1.insert_text((r_addr.x0, r_addr.y1), l1, fontname="helv", fontsize=5.8, color=(0,0,0))
            page1.insert_text((r_addr.x0, r_addr.y1 + 6.8), l2, fontname="helv", fontsize=5.8, color=(0,0,0))
        else:
            page1.insert_text((r_addr.x0, r_addr.y1), addr, fontname="helv", fontsize=5.8, color=(0,0,0))
            
    # Re-insert rotated Card Issue Date
    if issue_date_rects:
        r_iss = issue_date_rects[0]
        card_issue_str = f"Card Issue Date ({rc_data['tx_date']})"
        page1.insert_text((247.07, 140.40), card_issue_str, fontname="helv", fontsize=5.8, color=(0,0,0), rotate=270)

    # ------------ PAGE 2 (Back) ------------
    page2 = doc[1]
    
    p2_replacements = [
        ("AP39FE5474", rc_data["reg_no"], "hebo", 5.8),
        ("01-2020", rc_data["mfg_date"], "helv", 5.8),
        ("OTHERS", rc_data["maker_name"], "helv", 5.8),
        ("ACCESS 125", rc_data["model_name"], "helv", 5.8),
        ("PEARL MIRAGE WHITE", rc_data["colour"], "helv", 5.8),
        ("/ 2WN", f"/ {rc_data['body_type']}", "helv", 5.8),
        ("104", rc_data["unladen_wt"], "helv", 5.8),
        ("/ 254", f"/ {rc_data['laden_wt']}", "helv", 5.8),
        ("124.00", rc_data["cc"], "helv", 5.8),
        ("/ 6.4", f"/ {rc_data['hp']}", "helv", 5.8),
        ("/ 1265", f"/ {rc_data['wheelbase']}", "helv", 5.8),
        ("Amalapuram RTA", rc_data["authority"], "helv", 5.8),
    ]
    
    p2_actions = []
    for old_txt, new_txt, font, sz in p2_replacements:
        rects = page2.search_for(old_txt)
        for r in rects:
            p2_actions.append((r, old_txt, new_txt, font, sz))
            page2.add_redact_annot(r, fill=None)
            
    # Also replace QR code image on Page 2
    # In card.pdf, QR code is image #1 at rect (7.403, 43.185, 75.266, 111.048)
    qr_rect = fitz.Rect(7.403, 43.185, 75.266, 111.048)
    page2.add_redact_annot(qr_rect, fill=None)
    
    page2.apply_redactions()
    
    for r, old_txt, new_txt, font, sz in p2_actions:
        page2.insert_text((r.x0, r.y1), new_txt, fontname=font, fontsize=sz, color=(0,0,0))
        
    if os.path.exists(rc_data["qr_path"]):
        page2.insert_image(qr_rect, filename=rc_data["qr_path"])
        
    doc.save(output_pdf)
    print(f"Successfully converted RC card saved to {output_pdf}")


def convert_dl_card(dl_data, template_pdf="dl_card.pdf", output_pdf="dl_a4_converted_card.pdf"):
    doc = fitz.open(template_pdf)
    
    # ------------ PAGE 1 ------------
    page1 = doc[0]
    
    p1_replacements = [
        ("AP53720210030345", dl_data["dl_no"], "hebo", 7.0),
        ("28-01-2021", dl_data["issue_date"], "hebo", 6.0),
        ("17-06-2031", dl_data["validity_nt"], "hebo", 6.0),
        ("RAJESWARA RAO  ANEM", dl_data["name"], "hebo", 6.0),
        ("01-01-1962", dl_data["dob"], "hebo", 6.0),
        ("VEERAJU", dl_data["swd_of"], "hebo", 6.0),
        ("8-112,", dl_data["address"][:30], "hebo", 6.0),
        ("MAVULLAMMA STREET,", dl_data["address"][30:60] if len(dl_data["address"]) > 30 else "", "hebo", 6.0),
        ("MARUTERU,534122", dl_data["address"][60:] if len(dl_data["address"]) > 60 else "", "hebo", 6.0),
    ]
    
    p1_actions = []
    for old_txt, new_txt, font, sz in p1_replacements:
        if not old_txt.strip(): continue
        rects = page1.search_for(old_txt)
        for r in rects:
            p1_actions.append((r, old_txt, new_txt, font, sz))
            page1.add_redact_annot(r, fill=None)
            
    # Redact photo area on DL card Page 1 (bbox: 33.0, 16.0, 73.0, 56.0 or 185, 33, 225, 83)
    photo_rect = fitz.Rect(185.0, 33.0, 225.0, 83.0)
    # Wait! On dl_card page 1, photo is placed at (185, 33, 225, 83)
    page1.add_redact_annot(photo_rect, fill=None)
    
    page1.apply_redactions()
    
    for r, old_txt, new_txt, font, sz in p1_actions:
        page1.insert_text((r.x0, r.y1), new_txt, fontname=font, fontsize=sz, color=(0,0,0))
        
    if os.path.exists(dl_data["photo_path"]):
        page1.insert_image(photo_rect, filename=dl_data["photo_path"])

    # ------------ PAGE 2 ------------
    page2 = doc[1]
    
    p2_replacements = [
        ("AP53720210030345", dl_data["dl_no"], "hebo", 7.0),
        ("28-01-2021", dl_data["issue_date"], "hebo", 5.0),
        ("AP537", dl_data["original_la"], "hebo", 5.0),
    ]
    
    p2_actions = []
    for old_txt, new_txt, font, sz in p2_replacements:
        rects = page2.search_for(old_txt)
        for r in rects:
            p2_actions.append((r, old_txt, new_txt, font, sz))
            page2.add_redact_annot(r, fill=None)
            
    # Redact QR code on page 2
    qr_rect = fitz.Rect(192.0, 28.0, 237.0, 62.0)
    page2.add_redact_annot(qr_rect, fill=None)
    
    page2.apply_redactions()
    
    for r, old_txt, new_txt, font, sz in p2_actions:
        page2.insert_text((r.x0, r.y1), new_txt, fontname=font, fontsize=sz, color=(0,0,0))
        
    if os.path.exists(dl_data["qr_path"]):
        page2.insert_image(qr_rect, filename=dl_data["qr_path"])
        
    doc.save(output_pdf)
    print(f"Successfully converted DL card saved to {output_pdf}")


if __name__ == "__main__":
    rc_data = parse_rc_a4("a4.pdf")
    convert_rc_card(rc_data, "card.pdf", "a4_converted_card.pdf")
    convert_rc_card(rc_data, "card.pdf", "card_converted.pdf")

    dl_data = parse_dl_a4("dl_a4.pdf")
    convert_dl_card(dl_data, "dl_card.pdf", "dl_a4_converted_card.pdf")
    convert_dl_card(dl_data, "dl_card.pdf", "dl_card_converted.pdf")
