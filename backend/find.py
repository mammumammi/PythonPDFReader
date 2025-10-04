# find.py
import pdfplumber
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
# ---------------- Google Sheets Setup ----------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Read credentials from environment variable
creds_json = os.environ.get("GOOGLE_CREDENTIALS")
creds_dict = json.loads(creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)
sheet = client.open("Insurance PDF Reader").sheet1
# ---------------- PDF Extraction ----------------
def extract_text_from_box(page, left, top, right, bottom):
    """
    Extracts text from a bounding box on a pdfplumber page.
    """
    cropped = page.crop((left, top, right, bottom))
    text = cropped.extract_text()
    return text.strip() if text else ""

def read_pdf(pdf_path):
    """
    Reads a PDF file and extracts all required fields.
    Returns a dictionary with the extracted data.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
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

    return data

def push_to_sheet(data):
    """
    Push extracted data to Google Sheets.
    """
    row = [data.get("PolicyNo",""), data.get("Insured",""), data.get("Address",""),
           data.get("POI",""), data.get("Intermediary",""), data.get("Telephone","")]
    sheet.append_row(row)
    print("Data pushed to Google Sheets:", row)
