"""
파일 변경을 감지하여 자동으로 git add, commit, push를 수행하는 백그라운드 스크립트입니다.
5초마다 git status를 확인하여 변경사항이 감지되면 자동으로 커밋 및 푸시합니다.
"""

import os
import subprocess
import time

def run_git_command(args):
    """Git 명령을 실행하고 결과를 반환합니다."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git 명령 실행 실패: {' '.join(args)}")
        print(f"오류 메시지: {e.stderr.strip()}")
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
        print("변경사항 감지! 자동 커밋 및 푸시를 시작합니다.")
        
        # 1. git add -A
        run_git_command(["add", "-A"])
        
        # 2. git commit
        # 커밋 메시지에 변경된 파일들의 정보를 간략하게 포함
        commit_msg = "auto: 파일 변경 사항 자동 커밋"
        run_git_command(["commit", "-m", commit_msg])
        
        # 3. git push origin main
        print("원격 저장소로 푸시 중...")
        run_git_command(["push", "origin", "main"])
        print("자동 커밋 및 푸시 완료.")

def main():
    print("자동 커밋 및 푸시 모니터링 시작 (주기: 5초)...")
    while True:
        try:
            auto_commit_push()
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n모니터링을 종료합니다.")
            break
        except Exception as e:
            print(f"실행 중 예외 발생: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
