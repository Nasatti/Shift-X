import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
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
    extract_pdf_text(
        r"C:\Users\giack\Desktop\Progetto TedX\Compiti_selezionati_(anni precedenti)\TedGo_Compito4.pdf",
        r"C:\Users\giack\.gemini\antigravity\scratch\shift_x_flutter\TedGo_Compito4.txt"
    )
