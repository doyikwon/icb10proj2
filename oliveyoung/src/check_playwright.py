"""
플레이라이트(Playwright) 라이브러리가 설치되어 있는지 확인하고 사용 가능 여부를 점검하는 스크립트입니다.
"""

import sys

try:
    import playwright
    print("Playwright is installed.")
except ImportError:
    print("Playwright is NOT installed.")
