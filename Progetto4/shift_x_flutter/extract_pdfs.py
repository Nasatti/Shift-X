import os
import sys

try:
    import pypdf
except ImportError:
    print("pypdf is not installed. Trying to install it...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
    import pypdf

def extract_pdf_text(pdf_path, txt_path):
    print(f"Extracting {pdf_path} to {txt_path}...")
    try:
        reader = pypdf.PdfReader(pdf_path)
        print(f"Total pages: {len(reader.pages)}")
        with open(txt_path, "w", encoding="utf-8") as f:
            for idx, page in enumerate(reader.pages):
                text = page.extract_text()
                f.write(f"--- PAGE {idx + 1} ---\n")
                f.write(text + "\n\n")
        print("Extraction complete!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Extract presentation
    extract_pdf_text(
        r"C:\Users\giack\Desktop\Shift-X\Consegna\Progetto-1\SHIFT-X - Presentazione.pdf",
        r"C:\Users\giack\.gemini\antigravity\scratch\shift_x_flutter\SHIFT-X_Presentazione.txt"
    )
    
    # Extract homework/project instructions
    extract_pdf_text(
        r"C:\Users\giack\Desktop\Shift-X\Materiale\Progetto4\11_Flutter_App (1).pdf",
        r"C:\Users\giack\.gemini\antigravity\scratch\shift_x_flutter\11_Flutter_App_1.txt"
    )
    
    extract_pdf_text(
        r"C:\Users\giack\Desktop\Shift-X\Materiale\Progetto4\11_Flutter_App (2).pdf",
        r"C:\Users\giack\.gemini\antigravity\scratch\shift_x_flutter\11_Flutter_App_2.txt"
    )
