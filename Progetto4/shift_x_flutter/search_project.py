import os
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pypdf

def search_text_in_pdf(pdf_path, query_regex):
    matches = []
    try:
        reader = pypdf.PdfReader(pdf_path)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue
            for line_num, line in enumerate(text.split('\n')):
                if query_regex.search(line):
                    matches.append((page_num + 1, line_num + 1, line.strip()))
    except Exception as e:
        pass
    return matches

def search_text_in_file(file_path, query_regex):
    matches = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f):
                if query_regex.search(line):
                    matches.append((line_num + 1, line.strip()))
    except Exception as e:
        pass
    return matches

def main():
    search_dirs = [
        r"C:\Users\giack\Desktop\Shift-X",
        r"C:\Users\giack\Desktop\Progetto TedX",
        r"C:\Users\giack\Desktop\App_Flutter_Cloud"
    ]
    
    # We want to find references to Career-Path, Carrer-Path, career, carrer, api endpoints
    query_regex = re.compile(r'execute-api|career-path|carrer-path|career|carrer|lambda|url|http', re.IGNORECASE)
    
    print("Searching for project references...")
    for directory in search_dirs:
        print(f"Scanning {directory}...")
        for root, dirs, files in os.walk(directory):
            # Skip node_modules, build, etc.
            if any(p in root.lower() for p in ['node_modules', '.dart_tool', 'build', 'android', 'ios', '.git']):
                continue
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                path = os.path.join(root, file)
                if ext == '.pdf':
                    pdf_matches = search_text_in_pdf(path, query_regex)
                    if pdf_matches:
                        print(f"\n[PDF] {path}:")
                        for page, line_no, line in pdf_matches[:10]:
                            print(f"  Page {page}, Line {line_no}: {line}")
                elif ext in ['.txt', '.py', '.js', '.dart', '.json', '.yaml', '.md']:
                    file_matches = search_text_in_file(path, query_regex)
                    if file_matches:
                        print(f"\n[FILE] {path}:")
                        for line_no, line in file_matches[:10]:
                            print(f"  Line {line_no}: {line}")

if __name__ == '__main__':
    main()
