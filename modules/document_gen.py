# modules/document_gen.py
from docx import Document
from docx.shared import RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_final_docx(path, char_name, intro_text, infobox_raw, body_text, original_url):
    """Tạo file Word cuối cùng"""
    doc = Document()
    
    # 1. TITLE
    main_title = doc.add_heading(f"{char_name} | Wiki nhân vật Game of Thrones", level=0)
    main_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("\n")

    # 2. INTRO
   # ... (Code phần 1. TITLE giữ nguyên) ...

    # 2. INTRO
    if intro_text:
        p = doc.add_paragraph() # Tạo paragraph trống trước
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        # Xử lý In Đậm (**) và In Nghiêng (*) cho phần Intro
        parts = intro_text.split('**')
        for i, part in enumerate(parts):
            # i lẻ -> Nằm giữa cặp ** -> In Đậm
            if i % 2 != 0: 
                run = p.add_run(part)
                run.bold = True
                run.font.color.rgb = RGBColor(0, 0, 0)
            # i chẵn -> Văn bản thường (hoặc chứa in nghiêng)
            else:
                # Xử lý In Nghiêng (*) lồng bên trong
                sub_parts = part.split('*')
                for j, sub_part in enumerate(sub_parts):
                    run = p.add_run(sub_part)
                    if j % 2 != 0: # j lẻ -> In Nghiêng
                        run.italic = True
    
    doc.add_paragraph("\n")

    # ... (Code phần 3. INFOBOX TABLE giữ nguyên) ...

    # 3. INFOBOX TABLE
    if infobox_raw:
        doc.add_heading(f'Tổng quan về {char_name}', level=1)
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        table.rows[0].cells[0].text = 'Thông tin'
        table.rows[0].cells[1].text = 'Chi Tiết'
        
        for line in infobox_raw.split('\n'):
            if '|' in line:
                key, val = line.split('|', 1)
                if key.strip() and val.strip():
                    row = table.add_row()
                    row.cells[0].text = f"✅ {key.strip()}"
                    row.cells[1].text = f"⭐ {val.strip()}"
        doc.add_paragraph("\n")

    # 4. BODY
    # ... (Các phần code phía trên giữ nguyên) ...

    # 4. BODY
    doc.add_heading('Nội dung chi tiết', level=1)
    for line in body_text.split('\n'):
        line = line.strip()
        if not line: continue
        
        if line.startswith('### '): doc.add_heading(line[4:], level=3)
        elif line.startswith('## '): doc.add_heading(line[3:], level=2)
        elif line.startswith('# '): doc.add_heading(line[2:], level=1)
        else:
            p = doc.add_paragraph()
            # Tách phần In đậm (**) trước
            parts = line.split('**')
            for i, part in enumerate(parts):
                # Nếu i lẻ -> Nằm giữa cặp ** -> Xử lý In Đậm
                if i % 2 != 0: 
                    run = p.add_run(part)
                    run.bold = True
                    run.font.color.rgb = RGBColor(0, 0, 0)
                
                # Nếu i chẵn -> Văn bản thường hoặc chứa In Nghiêng (*)
                else:
                    # Tách tiếp phần In nghiêng (*) trong đoạn văn bản này
                    sub_parts = part.split('*')
                    for j, sub_part in enumerate(sub_parts):
                        run = p.add_run(sub_part)
                        # Nếu j lẻ -> Nằm giữa cặp * -> Xử lý In Nghiêng
                        if j % 2 != 0:
                            run.italic = True

    # ... (Phần code FOOTER phía dưới giữ nguyên) ...

    # 5. FOOTER
    doc.add_paragraph("\n")
    doc.add_heading('Thư Viện Ảnh', level=2)
    doc.add_paragraph('[gallery link="file" columns="2" size="medium" ids="..."]')
    doc.add_paragraph("---")
    
    footer = doc.add_paragraph()
    footer.add_run(f'Các bạn đang theo dõi bài viết “{char_name} | Wiki nhân vật Game of Thrones”...')
    footer.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    ref = doc.add_paragraph()
    ref.add_run("Nguồn tham khảo:").bold = True
    ref.add_run(f"\n{char_name} - {original_url}")

    doc.save(path)