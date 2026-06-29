import os

def list_all_files(root_dir):
    print(f"Listing all files in {root_dir}:")
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            path = os.path.join(root, file)
            try:
                size = os.path.getsize(path)
                print(f"{path} - {size} bytes")
            except Exception as e:
                print(f"Error reading size for {path}: {e}")

if __name__ == "__main__":
    list_all_files(r"C:\Users\giack\Desktop\Shift-X")
