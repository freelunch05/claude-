#!/usr/bin/env python3
"""
Appium으로 삼성증권 POP 앱을 실행 → (필요시) PIN 자동 로그인 →
신용현황 화면으로 이동 → 화면 캡처 → OCR로 신용액 추출/기록.

사전 준비:
  1. `python credentials.py setup` 으로 ID/PIN을 암호화 저장해둔다.
  2. `ui_steps.example.json` 을 복사해 `ui_steps.json` 을 만들고,
     Appium Inspector로 실제 앱을 열어 요소 id/텍스트를 채운다.
  3. 로컬에서 Appium 서버를 띄우고 폰을 USB로 연결한다.
     appium

이 스크립트는 이미 만들어둔 capture_credit_balance.py의 OCR 로직을 재사용한다.
"""

import argparse
import json
import sys
import time
from pathlib import Path

try:
    from appium import webdriver
    from appium.options.android import UiAutomator2Options
    from appium.webdriver.common.appiumby import AppiumBy
except ImportError:
    print("필요한 패키지가 없습니다: pip install Appium-Python-Client")
    sys.exit(1)

from capture_credit_balance import append_log, extract_credit_amount, ocr_text
from credentials import load_credentials

DEFAULT_STEPS_PATH = Path(__file__).parent / "ui_steps.json"
DEFAULT_LOG = Path(__file__).parent / "credit_balance_log.csv"


def load_steps(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} 가 없습니다. ui_steps.example.json 을 복사해서 값을 채워주세요."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def build_driver(appium_url: str, app_package: str, app_activity: str):
    options = UiAutomator2Options()
    options.app_package = app_package
    options.app_activity = app_activity
    options.no_reset = True  # 기존 로그인 세션이 있으면 유지
    return webdriver.Remote(appium_url, options=options)


def element_present(driver, by: str, value: str, timeout: float = 3.0) -> bool:
    by_map = {"id": AppiumBy.ID, "xpath": AppiumBy.XPATH, "text": AppiumBy.ANDROID_UIAUTOMATOR}
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if by == "text":
                driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'text("{value}")')
            else:
                driver.find_element(by_map[by], value)
            return True
        except Exception:
            time.sleep(0.3)
    return False


def run_steps(driver, steps: list, pin: str | None = None) -> None:
    for step in steps:
        action = step["action"]
        if action == "wait":
            time.sleep(step["seconds"])
        elif action == "tap_id":
            driver.find_element(AppiumBy.ID, step["value"]).click()
        elif action == "tap_xpath":
            driver.find_element(AppiumBy.XPATH, step["value"]).click()
        elif action == "tap_text":
            driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'text("{step["value"]}")').click()
        elif action == "type_pin_digits":
            if pin is None:
                raise ValueError("type_pin_digits 에는 PIN이 필요합니다.")
            template = step["digit_id_template"]
            for digit in pin:
                driver.find_element(AppiumBy.ID, template.format(d=digit)).click()
                time.sleep(0.2)
        else:
            raise ValueError(f"알 수 없는 action: {action}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--appium-url", default="http://127.0.0.1:4723")
    parser.add_argument("--steps", type=Path, default=DEFAULT_STEPS_PATH)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--keep-screenshot", action="store_true")
    args = parser.parse_args()

    config = load_steps(args.steps)
    creds = load_credentials()

    driver = build_driver(args.appium_url, config["app_package"], config["app_activity"])
    try:
        login_check = config["login_check"]
        if element_present(driver, login_check["by"], login_check["value"]):
            print("로그인 화면 감지, PIN 입력 중...")
            run_steps(driver, config["login_steps"], pin=creds["pin"])
        else:
            print("이미 로그인된 상태로 보입니다.")

        print("신용현황 화면으로 이동 중...")
        run_steps(driver, config["navigate_steps"])

        screenshot_path = Path(f"screen_{int(time.time())}.png")
        driver.get_screenshot_as_file(str(screenshot_path))

        print("OCR 인식 중...")
        text = ocr_text(screenshot_path)
        amount = extract_credit_amount(text)
        if amount:
            print(f"신용액: {int(amount):,}원")
        else:
            print("신용액을 자동으로 찾지 못했습니다. OCR 결과:")
            print(text)

        append_log(args.log, amount, text)
        print(f"기록됨: {args.log}")

        if not args.keep_screenshot:
            screenshot_path.unlink(missing_ok=True)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
