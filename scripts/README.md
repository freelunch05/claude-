# 삼성증권 신용액 캡처 스크립트

삼성증권은 리테일용 오픈 API를 제공하지 않아, 모바일 앱(POP) 화면을
캡처하고 OCR로 읽어 신용거래융자금(신용액)을 기록하는 방식입니다.

로그인과 화면 이동은 자동화하지 않습니다. 로그인 자동화는 계정 보안·약관
리스크가 크고 생체인증/OTP 때문에 안정적으로 동작하기도 어렵습니다.
대신 사용자가 직접 로그인해서 신용액이 보이는 화면을 띄운 상태에서
스크립트를 실행하면, 그 화면을 캡처해 숫자를 뽑아 CSV에 기록합니다.

## 준비물

- USB 케이블로 PC에 연결한 안드로이드 폰 (USB 디버깅 활성화)
- `adb` (Android SDK Platform Tools)
- Python 3.10+
- `tesseract-ocr` + 한국어 언어팩(`tesseract-ocr-kor`)

```bash
# 예: Ubuntu/Debian
sudo apt-get install adb tesseract-ocr tesseract-ocr-kor

pip install pytesseract pillow
```

## 사용법

1. 폰을 USB로 연결하고 `adb devices`로 인식되는지 확인합니다.
2. 삼성증권 POP 앱을 열고 로그인한 뒤, 신용액이 보이는 화면
   (예: 신용현황, 신용잔고 조회 등)으로 이동합니다.
3. 아래 명령을 실행합니다.

```bash
python scripts/capture_credit_balance.py
```

실행하면 현재 화면을 캡처해 OCR로 "신용" 뒤에 오는 금액 숫자를 찾고,
`scripts/credit_balance_log.csv`에 시간과 함께 기록합니다.
숫자를 자동으로 못 찾으면 OCR 전체 텍스트를 출력해주니, 그걸 보고
직접 값을 확인하거나 화면/정규식을 조정하면 됩니다.

## 참고

- 기기에 화면 잠금이 걸려 있으면 캡처가 안 됩니다.
- OCR 인식률은 폰 해상도/폰트 크기에 따라 달라질 수 있습니다.
  `--keep-screenshot` 옵션을 주면 캡처된 이미지를 남겨서 확인할 수 있습니다.
- 신용액 표시 형식이 앱과 다르면 `AMOUNT_PATTERN` 정규식을 화면에 맞게 수정하세요.
