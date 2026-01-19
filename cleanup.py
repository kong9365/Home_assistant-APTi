"""불필요한 파일 정리 스크립트.

GitHub에 올릴 때 필요한 파일만 남기고 나머지를 삭제합니다.
실행: python cleanup.py
"""

import os
import shutil

# 현재 디렉토리
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 유지할 파일 목록
KEEP_FILES = {
    # 핵심 코드
    "__init__.py",
    "api.py",
    "config_flow.py",
    "const.py",
    "coordinator.py",
    "entity.py",
    "sensor.py",
    "apti_parser.py",
    "helper.py",

    # 설정 파일
    "manifest.json",
    "strings.json",
    "requirements.txt",

    # 문서
    "README.md",
    "SETUP_GUIDE.md",

    # Git
    ".gitignore",

    # 이 스크립트
    "cleanup.py",
}

# 유지할 폴더 목록
KEEP_DIRS = {
    ".github",
    "translations",
    "icons",
}

# 삭제할 파일 패턴
DELETE_PATTERNS = [
    "*.html",
    "*.jpg",
    "*.png",
    "test_*.py",
    "debug_*.py",
    "analyze_*.py",
    "*_test.py",
    "*_debug.py",
    "parsing_result_*.json",
    "playwright_result_*.json",
    "pw_*.html",
    "html_*.html",
    "html_*.json",
]


def should_keep(filename: str) -> bool:
    """파일을 유지해야 하는지 확인."""
    return filename in KEEP_FILES


def cleanup():
    """불필요한 파일 정리."""
    deleted_files = []
    deleted_dirs = []

    for item in os.listdir(BASE_DIR):
        item_path = os.path.join(BASE_DIR, item)

        if os.path.isfile(item_path):
            if not should_keep(item):
                # .gitignore에 의해 무시될 파일들 삭제
                ext = os.path.splitext(item)[1]
                if ext in [".html", ".jpg", ".png", ".txt"] and item != "requirements.txt":
                    deleted_files.append(item)
                    os.remove(item_path)
                    continue

                if item.endswith(".md") and item not in ["README.md", "SETUP_GUIDE.md"]:
                    deleted_files.append(item)
                    os.remove(item_path)
                    continue

                if item.startswith(("test_", "debug_", "analyze_")) and item.endswith(".py"):
                    deleted_files.append(item)
                    os.remove(item_path)
                    continue

                if item.endswith(".json") and item not in ["manifest.json", "strings.json"]:
                    if "result" in item or "analysis" in item:
                        deleted_files.append(item)
                        os.remove(item_path)
                        continue

        elif os.path.isdir(item_path):
            if item not in KEEP_DIRS and item != "__pycache__":
                continue
            if item == "__pycache__":
                deleted_dirs.append(item)
                shutil.rmtree(item_path)

    print("=" * 50)
    print("정리 완료!")
    print("=" * 50)

    if deleted_files:
        print(f"\n삭제된 파일 ({len(deleted_files)}개):")
        for f in sorted(deleted_files):
            print(f"  - {f}")

    if deleted_dirs:
        print(f"\n삭제된 폴더 ({len(deleted_dirs)}개):")
        for d in sorted(deleted_dirs):
            print(f"  - {d}/")

    # 남은 파일 목록
    remaining = []
    for item in os.listdir(BASE_DIR):
        item_path = os.path.join(BASE_DIR, item)
        if os.path.isfile(item_path):
            remaining.append(item)
        elif os.path.isdir(item_path):
            remaining.append(f"{item}/")

    print(f"\n남은 항목 ({len(remaining)}개):")
    for item in sorted(remaining):
        print(f"  - {item}")


if __name__ == "__main__":
    print("APT.i Custom Component 정리 스크립트")
    print("=" * 50)
    response = input("불필요한 파일을 삭제하시겠습니까? (y/N): ").strip().lower()
    if response == "y":
        cleanup()
    else:
        print("취소되었습니다.")
