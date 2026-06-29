import os
import re
import pypdf
import sys
sys.stdout.reconfigure(encoding='utf-8')

def main():
    pdf_path = r"C:\Users\giack\Desktop\Progetto TedX\Compiti_selezionati_(anni precedenti)\Homework_3_Allievi_Fanton.pdf"
    print(f"Reading {pdf_path}...")
    try:
        reader = pypdf.PdfReader(pdf_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue
            if 'lambda' in text.lower() or 'api' in text.lower() or 'path' in text.lower() or 'carrer' in text.lower() or 'career' in text.lower():
                print(f"\n--- PAGE {i+1} ---")
                lines = text.split('\n')
                for line in lines:
                    if any(w in line.lower() for w in ['url', 'lambda', 'post', 'get', 'api', 'http', 'body', 'input', 'output']):
                        print(f"  {line.strip()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
