import os
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

def search_text_in_file(file_path, query_regex):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if query_regex.search(content):
                return content
    except Exception as e:
        pass
    return None

def main():
    brain_dir = r"C:\Users\giack\.gemini\antigravity\brain"
    # We search for Carrer-Path-master or Career-Path-master or similar, or the actual code of a lambda function.
    query_regex = re.compile(r'Carrer-Path-master|Career-Path-master|mg839u1xy1|Get_Talks_By_Tag|lambda_get_career_path', re.IGNORECASE)
    
    print("Searching brain directory for past conversations related to the project...")
    for root, dirs, files in os.walk(brain_dir):
        # We look for transcripts or source files in the brain folder
        for file in files:
            if file == 'transcript.jsonl' or file.endswith(('.py', '.js', '.dart', '.json', '.md', '.txt')):
                path = os.path.join(root, file)
                content = search_text_in_file(path, query_regex)
                if content:
                    print(f"\nFound match in file: {path}")
                    # Let's print some preview of matches
                    for line_no, line in enumerate(content.split('\n')):
                        if query_regex.search(line):
                            print(f"  Line {line_no+1}: {line[:120].strip()}")

if __name__ == '__main__':
    main()
