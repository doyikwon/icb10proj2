"""
Antigravity IDE 내부의 agy.exe 파일을 찾아 AppData 로컬 폴더에 재설치하는 스크립트입니다.
"""

import os
import shutil
import subprocess

def find_source_agy():
    search_root = r"C:\Users\doyik\AppData\Local\Programs\Antigravity IDE"
    print(f"Searching for agy.exe in: {search_root}")
    for root, dirs, files in os.walk(search_root):
        if "agy.exe" in files:
            path = os.path.join(root, "agy.exe")
            print(f"Found source agy.exe at: {path}")
            return path
    return None

def main():
    # 1. Kill running agy.exe processes
    print("Terminating running agy.exe processes...")
    subprocess.run(["taskkill", "/f", "/im", "agy.exe"], capture_output=True)
    
    # 2. Find source
    src = find_source_agy()
    if not src:
        print("Source agy.exe not found!")
        return
        
    # 3. Define destination
    dst = r"C:\Users\doyik\AppData\Local\agy\bin\agy.exe"
    print(f"Target path: {dst}")
    
    # 4. Copy file
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst):
            os.remove(dst)
            print("Removed existing target file.")
            
        shutil.copy2(src, dst)
        print("Reinstallation completed successfully!")
        print(f"Target file exists: {os.path.exists(dst)}, size: {os.path.getsize(dst)}")
    except Exception as e:
        print(f"Error occurred during reinstallation: {e}")

if __name__ == "__main__":
    main()
