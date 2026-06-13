"""
Antigravity IDE 내부의 agy.exe 파일을 전체 사용자 폴더에서 찾아 AppData 로컬 폴더에 확실하게 재설치하는 스크립트입니다.
"""

import os
import shutil
import subprocess

def main():
    # 1. Kill running agy.exe processes
    print("Terminating running agy.exe processes...")
    subprocess.run(["taskkill", "/f", "/im", "agy.exe"], capture_output=True)
    
    # 2. Search path under user profile
    p = os.environ.get("USERPROFILE", "C:/Users/doyik")
    print(f"Scanning for agy.exe under: {p}")
    src = None
    for r, d, files in os.walk(p):
        # Skip directories to speed up and avoid copying already-installed or ignored directories
        if "onedrive" in r.lower() or ".venv" in r.lower() or "appdata/local/agy" in r.lower().replace("\\", "/"):
            continue
        for f in files:
            if f.lower() == "agy.exe":
                src = os.path.join(r, f)
                break
        if src:
            break
            
    print(f"Found src: {src}")
    
    # 3. Copy if found
    if src:
        dst = "C:/Users/doyik/AppData/Local/agy/bin/agy.exe"
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copy2(src, dst)
        print(f"Reinstalled successfully! Exists: {os.path.exists(dst)}")
    else:
        print("Source agy.exe not found!")

if __name__ == "__main__":
    main()
