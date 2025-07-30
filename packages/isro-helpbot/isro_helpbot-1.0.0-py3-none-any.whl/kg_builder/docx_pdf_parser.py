import os
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document

# ----------------------------
# PDF Parser
# ----------------------------
def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"[ERROR] Failed to read PDF: {file_path}, reason: {e}")
        return ""

# ----------------------------
# DOCX Parser
# ----------------------------
def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"[ERROR] Failed to read DOCX: {file_path}, reason: {e}")
        return ""

# ----------------------------
# Excel Parser
# ----------------------------
def extract_text_from_excel(file_path):
    try:
        text_data = []
        excel_file = pd.ExcelFile(file_path)
        for sheet_name in excel_file.sheet_names:
            df = excel_file.parse(sheet_name)
            for row in df.values:
                for cell in row:
                    if isinstance(cell, str):
                        text_data.append(cell)
        return " ".join(text_data).strip()
    except Exception as e:
        print(f"[ERROR] Failed to read Excel: {file_path}, reason: {e}")
        return ""
