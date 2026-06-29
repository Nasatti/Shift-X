import os
import shutil

def copy_project():
    src = r"C:\Users\giack\Desktop\App_Flutter_Cloud\flutter_application_1"
    dst = r"C:\Users\giack\.gemini\antigravity\scratch\shift_x_flutter"
    
    print(f"Copying project from {src} to {dst}...")
    
    # Ignore build, .dart_tool, .idea, and android/ios build artifacts if any
    ignore_patterns = shutil.ignore_patterns('build', '.dart_tool', '.idea', 'ios', 'android', 'windows', 'linux', 'macos', 'web')
    
    # We will copy the lib folder, pubspec.yaml, analysis_options.yaml, etc.
    # For android/ios/etc, we can copy them but we want to ignore large build dirs.
    # Let's copy files one by one or use copytree with custom ignore.
    if os.path.exists(dst):
        # Keep extract_pdfs.py etc, but delete other things if needed. We can just overwrite
        pass
        
    for item in os.listdir(src):
        s_item = os.path.join(src, item)
        d_item = os.path.join(dst, item)
        
        if os.path.isdir(s_item):
            if item in ['build', '.dart_tool', '.idea']:
                continue
            if os.path.exists(d_item):
                shutil.rmtree(d_item)
            shutil.copytree(s_item, d_item)
        else:
            if item in ['pubspec.lock']:
                continue
            shutil.copy2(s_item, d_item)
            
    print("Project copied successfully!")

if __name__ == '__main__':
    copy_project()
