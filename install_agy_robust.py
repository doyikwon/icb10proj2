"""
Antigravity IDE 설치 폴더에서 agy.exe 파일을 안전하고 확실하게 찾아 복사하는 복구용 스크립트입니다.
"""

import os
import shutil
import subprocess

def walk_error_handler(err):
    # 권한 오류 등의 예외 발생 시 무시하고 진행
    pass

def main():
    print("Terminating running agy.exe processes...")
    subprocess.run(["taskkill", "/f", "/im", "agy.exe"], capture_output=True)
    
    # 윈도우 환경변수에서 로컬 프로그램 폴더 경로 획득
    local_app_data = os.environ.get("LOCALAPPDATA", r"C:\Users\doyik\AppData\Local")
    search_path = os.path.join(local_app_data, "Programs", "Antigravity IDE")
    
    print(f"Targeting search path: {search_path}")
    src = None
    
    if os.path.exists(search_path):
        for root, dirs, files in os.walk(search_path, onerror=walk_error_handler):
            for f in files:
                if f.lower() == "agy.exe":
                    src = os.path.join(root, f)
                    break
            if src:
                break
                
    print(f"Resolved source path: {src}")
    
    if src:
        dst = os.path.join(local_app_data, "agy", "bin", "agy.exe")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copy2(src, dst)
        print(f"SUCCESS: Reinstalled agy.exe. Exists: {os.path.exists(dst)}, Size: {os.path.getsize(dst)}")
    else:
        print("ERROR: Source agy.exe not found anywhere under Programs/Antigravity IDE!")

if __name__ == "__main__":
    main()
