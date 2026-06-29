import os
import re
import pypdf
import sys
sys.stdout.reconfigure(encoding='utf-8')

def search_in_pdf(pdf_path, regex):
    matches = []
    try:
        reader = pypdf.PdfReader(pdf_path)
        for idx, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue
            lines = text.split('\n')
            for line_no, line in enumerate(lines):
                if regex.search(line):
                    matches.append((idx + 1, line_no + 1, line.strip()))
    except Exception as e:
        pass
    return matches

def main():
    directory = r"C:\Users\giack\Desktop\Progetto TedX\Compiti_selezionati_(anni precedenti)"
    regex = re.compile(r'career|carrer|path|bedrock|generative|playlist', re.IGNORECASE)
    
    print(f"Scanning PDFs in {directory}...")
    for file in os.listdir(directory):
        if file.lower().endswith('.pdf'):
            path = os.path.join(directory, file)
            matches = search_in_pdf(path, regex)
            if matches:
                print(f"\n==========================================")
                print(f"File: {file}")
                print(f"Found {len(matches)} matches")
                for page, line_no, text in matches[:8]:
                    print(f"  P.{page} L.{line_no}: {text}")

if __name__ == '__main__':
    main()
