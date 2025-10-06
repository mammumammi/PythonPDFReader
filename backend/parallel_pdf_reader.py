# parallel_pdf_reader.py

import os
import json
import pdfplumber
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------------- Google Sheets Setup ----------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Make sure you set the GOOGLE_CREDENTIALS environment variable before running
creds_json = os.environ.get("GOOGLE_CREDENTIALS")
if not creds_json:
    raise EnvironmentError("Please set the GOOGLE_CREDENTIALS environment variable")

creds_dict = json.loads(creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("Insurance PDF Reader").sheet1

# ---------------- PDF Extraction ----------------
def extract_text_from_box(page, left, top, right, bottom):
    cropped = page.crop((left, top, right, bottom))
    text = cropped.extract_text()
    return text.strip() if text else ""

def read_pdf(pdf_path):
    """Reads a single PDF and returns a dictionary of extracted data."""
    data = {}
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[4]  # Page 5 (0-indexed)
            data = {
                "PolicyNo": extract_text_from_box(page, 115, 154, 250, 160),
                "Insured": extract_text_from_box(page, 115, 165, 300, 180),
                "Address": extract_text_from_box(page, 115, 185, 250, 250),
                "POI": extract_text_from_box(page, 390, 154, 550, 190),
                "Intermediary": extract_text_from_box(page, 380, 220, 550, 230),
                "Telephone": extract_text_from_box(page, 380, 260, 550, 262),
            }
        print(f"Finished reading: {os.path.basename(pdf_path)}")
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return data

def push_to_sheet(data):
    """Push a single row to Google Sheets."""
    if not data:
        return
    row = [
        data.get("PolicyNo", ""),
        data.get("Insured", ""),
        data.get("Address", ""),
        data.get("POI", ""),
        data.get("Intermediary", ""),
        data.get("Telephone", "")
    ]
    sheet.append_row(row)
    print(f"Pushed to Google Sheets: {row}")

def parallel_read_pdfs(folder_path, max_workers=8):
    """Reads all PDFs in folder in parallel and pushes them to Google Sheets."""
    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".pdf")]
    if not pdf_files:
        print("No PDF files found in folder:", folder_path)
        return
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_pdf = {executor.submit(read_pdf, pdf): pdf for pdf in pdf_files}
        for future in as_completed(future_to_pdf):
            pdf_path = future_to_pdf[future]
            try:
                data = future.result()
                push_to_sheet(data)
            except Exception as e:
                print(f"Error processing {pdf_path}: {e}")

if __name__ == "__main__":
    folder_path = "pdfs"  # Folder where PDFs are stored
    parallel_read_pdfs(folder_path, max_workers=8)
