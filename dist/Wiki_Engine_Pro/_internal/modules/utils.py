# modules/utils.py
import re

def sanitize_filename(name):
    """Làm sạch tên file để lưu trên Windows/Linux"""
    name = str(name).strip()
    return re.sub(r'[\\/*?:"<>|]', "", name)

def split_text(text, max_length=6000):
    """Chia nhỏ văn bản để tránh quá tải token"""
    paragraphs = text.split('\n\n')
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) < max_length:
            current += p + "\n\n"
        else:
            chunks.append(current)
            current = p + "\n\n"
    if current: chunks.append(current)
    return chunks