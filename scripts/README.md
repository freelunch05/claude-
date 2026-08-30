# 삼성증권 신용액 캡처 스크립트

삼성증권은 리테일용 오픈 API를 제공하지 않아, 모바일 앱(POP) 화면을
캡처하고 OCR로 읽어 신용거래융자금(신용액)을 기록하는 방식입니다.

두 가지 스크립트가 있습니다.

- `capture_credit_balance.py`: 로그인/화면 이동은 사람이 직접 하고,
  현재 떠 있는 화면만 캡처해 OCR로 읽는 수동 보조 버전.
- `auto_login_capture.py`: Appium으로 앱 실행 → 간편비밀번호(PIN)
  자동 입력 로그인 → 신용현황 화면 이동 → 캡처/OCR까지 전 과정 자동화.

주의: 로그인 자동화는 계정 보안·앱 약관상 리스크가 있습니다(자동화
접근으로 인한 이상거래 탐지/제한 가능성). 자동 로그인을 쓰기로
하셨다면 이 리스크를 감수하는 것으로 이해하고 진행합니다.

## 공통 준비물

- USB 케이블로 PC에 연결한 안드로이드 폰 (USB 디버깅 활성화)
- `adb` (Android SDK Platform Tools)
- Python 3.10+
- `tesseract-ocr` + 한국어 언어팩(`tesseract-ocr-kor`)

```bash
# 예: Ubuntu/Debian
sudo apt-get install adb tesseract-ocr tesseract-ocr-kor

pip install -r requirements.txt
```

## 수동 캡처 사용법 (capture_credit_balance.py)

1. 폰을 USB로 연결하고 `adb devices`로 인식되는지 확인합니다.
2. 삼성증권 POP 앱을 열고 직접 로그인한 뒤, 신용액이 보이는 화면
   (예: 신용현황, 신용잔고 조회 등)으로 이동합니다.
3. 아래 명령을 실행합니다.

```bash
python scripts/capture_credit_balance.py
```

실행하면 현재 화면을 캡처해 OCR로 "신용" 뒤에 오는 금액 숫자를 찾고,
`scripts/credit_balance_log.csv`에 시간과 함께 기록합니다.
숫자를 자동으로 못 찾으면 OCR 전체 텍스트를 출력해주니, 그걸 보고
직접 값을 확인하거나 화면/정규식을 조정하면 됩니다.

## 완전 자동화 사용법 (auto_login_capture.py)

추가로 필요한 것:

```bash
npm install -g appium
appium driver install uiautomator2
appium   # 별도 터미널에서 Appium 서버 실행
```

1. **자격증명 저장** (최초 1회, PIN은 화면에 표시되지 않고 로컬에 암호화 저장됨):
   ```bash
   python scripts/credentials.py setup
   ```
2. **앱 요소 정보 채우기**: `ui_steps.example.json` 을 복사해
   `ui_steps.json` 을 만든 뒤, [Appium Inspector](https://github.com/appium/appium-inspector)로
   실제 폰에 연결해 삼성증권 POP 앱의 패키지명/액티비티명, PIN 숫자
   버튼의 resource-id, "신용현황" 메뉴로 가는 탭 순서를 찾아 채웁니다.
   (이 부분은 앱 UI를 직접 봐야 알 수 있어서 자동으로 채워둘 수 없습니다.)
3. 실행:
   ```bash
   python scripts/auto_login_capture.py
   ```
   로그인 화면이 감지되면 저장해둔 PIN으로 자동 로그인하고, 신용현황
   화면까지 이동한 뒤 캡처/OCR/CSV 기록까지 한 번에 수행합니다.

## 참고

- 기기에 화면 잠금이 걸려 있으면 캡처가 안 됩니다.
- OCR 인식률은 폰 해상도/폰트 크기에 따라 달라질 수 있습니다.
  `--keep-screenshot` 옵션을 주면 캡처된 이미지를 남겨서 확인할 수 있습니다.
- 신용액 표시 형식이 앱과 다르면 `capture_credit_balance.py`의
  `AMOUNT_PATTERN` 정규식을 화면에 맞게 수정하세요.
- 자격증명은 `~/.config/samsung_pop/` 아래 암호화되어 저장되며,
  키 파일과 암호문 파일 모두 소유자만 읽을 수 있도록 권한이 제한됩니다.
