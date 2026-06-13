"""
파일 변경을 감지하여 자동으로 git add, commit, push를 수행하는 백그라운드 스크립트입니다.
윈도우 환경에서의 인코딩 문제를 방지하기 위해 표준 출력 로그는 영문으로 작성되었습니다.
"""

import os
import subprocess
import time

def run_git_command(args):
    """Git 명령을 실행하고 결과를 반환합니다."""
    try:
        # Windows git output encoding could be utf-8 or cp949. Specifying errors='replace' to avoid decoding errors.
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True,
            errors="replace"
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {' '.join(args)}")
        print(f"Error: {e.stderr.strip() if e.stderr else ''}")
        return None

def check_changes():
    """작업 디렉토리에 변경사항이 있는지 확인합니다."""
    status = run_git_command(["status", "--porcelain"])
    if status is None:
        return False
    return len(status) > 0

def auto_commit_push():
    """변경사항이 있을 경우 add, commit, push를 실행합니다."""
    if check_changes():
        print("Changes detected! Starting auto commit and push.")
        
        # 1. git add -A
        run_git_command(["add", "-A"])
        
        # 2. git commit
        commit_msg = "auto: auto commit on changes"
        run_git_command(["commit", "-m", commit_msg])
        
        # 3. git push origin main
        print("Pushing to remote origin main...")
        run_git_command(["push", "origin", "main"])
        print("Auto commit and push completed successfully.")

def main():
    print("Auto commit and push monitoring started (Interval: 5s)...")
    while True:
        try:
            auto_commit_push()
            time.sleep(5)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
            break
        except Exception as e:
            print(f"Exception occurred: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
