import fitz

def redact_and_replace_rc(template_pdf, a4_data, output_pdf):
    doc = fitz.open(template_pdf)
    
    # ---------------- PAGE 1 ----------------
    page1 = doc[0]
    
    # Text mapping for Page 1
    # Find spans to replace
    replacements_p1 = [
        ("AP39FE5474", a4_data["reg_no"]),
        ("24-Jul-2020", a4_data["reg_date"]),
        ("23-Jul-2035", a4_data["valid_upto"]),
        ("MB8DP12DAL8112956", a4_data["chassis_no"]),
        ("AF212262873", a4_data["engine_no"]),
        ("APPARI BHAVESH", a4_data["owner_name"]),
        ("APPARI PRASAD", a4_data["swd_of"]),
        ("7-21,KOTHAPALEM, MACHAVARAM, , KONASEEMA-ANDHRA PRADESH-", a4_data["address"][:55]),
        ("533214", a4_data["address"][55:] if len(a4_data["address"]) > 55 else ""),
        ("18-Jul-2026", a4_data["tx_date"])
    ]
    
    for old_text, new_text in replacements_p1:
        if not old_text.strip():
            continue
        text_instances = page1.search_for(old_text)
        for inst in text_instances:
            page1.add_redact_annot(inst, fill=None)
            
    page1.apply_redactions()
    
    # Now re-insert text
    for old_text, new_text in replacements_p1:
        if not old_text.strip() or not new_text.strip():
            continue
        text_instances = page1.search_for(old_text) # wait, old_text is gone, so let's find original rects BEFORE applying redaction!
        
doc = fitz.open("card.pdf")
page = doc[0]
rects = page.search_for("APPARI BHAVESH")
print("APPARI BHAVESH rect:", rects)
