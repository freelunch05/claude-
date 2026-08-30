#!/usr/bin/env python3
"""
삼성증권 POP 앱 신용현황 화면을 캡처해 신용액을 OCR로 읽어 기록한다.

사용법:
  1. 폰에서 USB 디버깅을 켜고 PC와 연결한다 (adb devices로 확인).
  2. 삼성증권 POP 앱에 로그인하고, 신용액이 보이는 화면(신용현황/신용잔고 등)을 띄운다.
  3. python capture_credit_balance.py 를 실행한다.

로그인/화면 이동은 자동화하지 않는다. 사용자가 직접 로그인한 뒤,
확인하고 싶은 화면을 띄운 상태에서 이 스크립트를 실행하는 것을 전제로 한다.
"""

import argparse
import csv
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    import pytesseract
    from PIL import Image
except ImportError:
    print("필요한 패키지가 없습니다. 다음을 실행하세요:")
    print("  pip install pytesseract pillow")
    print("  (그리고 시스템에 tesseract-ocr, tesseract-ocr-kor 설치 필요)")
    sys.exit(1)

DEFAULT_LOG = Path(__file__).parent / "credit_balance_log.csv"
# "신용" 이라는 단어 뒤에 금액 숫자가 나오는 패턴을 찾는다.
AMOUNT_PATTERN = re.compile(r"신용[^\d\-]{0,10}([\d,]{3,})")


def adb(*args: str, device: str | None = None) -> bytes:
    cmd = ["adb"]
    if device:
        cmd += ["-s", device]
    cmd += list(args)
    result = subprocess.run(cmd, capture_output=True, check=True)
    return result.stdout


def take_screenshot(out_path: Path, device: str | None = None) -> None:
    data = adb("exec-out", "screencap", "-p", device=device)
    out_path.write_bytes(data)


def ocr_text(image_path: Path) -> str:
    image = Image.open(image_path)
    return pytesseract.image_to_string(image, lang="kor+eng")


def extract_credit_amount(text: str) -> str | None:
    match = AMOUNT_PATTERN.search(text)
    if not match:
        return None
    return match.group(1).replace(",", "")


def append_log(log_path: Path, amount: str | None, raw_text: str) -> None:
    is_new = not log_path.exists()
    with log_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["timestamp", "credit_amount", "ocr_snippet"])
        snippet = " ".join(raw_text.split())[:200]
        writer.writerow([datetime.now().isoformat(timespec="seconds"), amount or "", snippet])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", help="adb 기기 시리얼 (여러 대 연결 시)")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG, help="결과를 저장할 CSV 경로")
    parser.add_argument("--keep-screenshot", action="store_true", help="캡처한 스크린샷 파일을 남긴다")
    args = parser.parse_args()

    screenshot_path = Path(f"screen_{datetime.now():%Y%m%d_%H%M%S}.png")

    print("화면 캡처 중...")
    take_screenshot(screenshot_path, device=args.device)

    print("OCR 인식 중...")
    text = ocr_text(screenshot_path)

    amount = extract_credit_amount(text)
    if amount:
        print(f"신용액: {int(amount):,}원")
    else:
        print("신용액을 자동으로 찾지 못했습니다. 아래 OCR 결과를 확인하세요:")
        print("-" * 40)
        print(text)
        print("-" * 40)

    append_log(args.log, amount, text)
    print(f"기록됨: {args.log}")

    if not args.keep_screenshot:
        screenshot_path.unlink(missing_ok=True)
    else:
        print(f"스크린샷 저장됨: {screenshot_path}")


if __name__ == "__main__":
    main()
