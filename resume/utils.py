# resumes/utils.py
from typing import IO
from docx import Document
from PyPDF2 import PdfReader

def extract_text_from_upload(f: IO) -> str:
    name = (getattr(f, 'name', '') or '').lower()
    # 重要：文件游标可能被多次读取，先把 bytes 取出再分支
    data = f.read()
    if name.endswith('.txt'):
        return data.decode('utf-8', errors='ignore')
    if name.endswith('.docx'):
        # python-docx 需要文件-like；用 BytesIO 包一下
        from io import BytesIO
        doc = Document(BytesIO(data))
        return '\n'.join(p.text for p in doc.paragraphs)
    if name.endswith('.pdf'):
        from io import BytesIO
        reader = PdfReader(BytesIO(data))
        return '\n'.join((page.extract_text() or '') for page in reader.pages)
    try:
        return data.decode('utf-8', errors='ignore')
    except Exception:
        return ''
