"""
간편비밀번호(PIN)를 로컬에 암호화 저장/조회한다.

- 대칭키는 별도 파일(key.key)로 관리, 파일 권한 600으로 제한.
- 절대 코드나 로그에 평문 PIN을 남기지 않는다.
"""

import argparse
import getpass
import json
import os
import stat
from pathlib import Path

from cryptography.fernet import Fernet

CONFIG_DIR = Path.home() / ".config" / "samsung_pop"
KEY_PATH = CONFIG_DIR / "key.key"
CREDS_PATH = CONFIG_DIR / "creds.enc"


def _ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(CONFIG_DIR, stat.S_IRWXU)  # 소유자만 접근 가능 (700)


def _load_or_create_key() -> bytes:
    _ensure_config_dir()
    if KEY_PATH.exists():
        return KEY_PATH.read_bytes()
    key = Fernet.generate_key()
    KEY_PATH.write_bytes(key)
    os.chmod(KEY_PATH, stat.S_IRUSR | stat.S_IWUSR)  # 600
    return key


def save_credentials(user_id: str, pin: str) -> None:
    _ensure_config_dir()
    key = _load_or_create_key()
    fernet = Fernet(key)
    payload = json.dumps({"user_id": user_id, "pin": pin}).encode("utf-8")
    encrypted = fernet.encrypt(payload)
    CREDS_PATH.write_bytes(encrypted)
    os.chmod(CREDS_PATH, stat.S_IRUSR | stat.S_IWUSR)  # 600


def load_credentials() -> dict:
    if not CREDS_PATH.exists() or not KEY_PATH.exists():
        raise FileNotFoundError(
            "저장된 자격증명이 없습니다. 먼저 python credentials.py setup 을 실행하세요."
        )
    key = KEY_PATH.read_bytes()
    fernet = Fernet(key)
    decrypted = fernet.decrypt(CREDS_PATH.read_bytes())
    return json.loads(decrypted.decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="삼성증권 POP 간편비밀번호 저장")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup", help="ID와 PIN을 입력받아 암호화 저장")
    sub.add_parser("show-id", help="저장된 ID만 확인 (PIN은 출력하지 않음)")
    args = parser.parse_args()

    if args.cmd == "setup":
        user_id = input("삼성증권 ID: ").strip()
        pin = getpass.getpass("간편비밀번호(PIN, 화면에 표시되지 않음): ").strip()
        save_credentials(user_id, pin)
        print(f"암호화 저장 완료: {CREDS_PATH}")
    elif args.cmd == "show-id":
        creds = load_credentials()
        print(f"저장된 ID: {creds['user_id']}")


if __name__ == "__main__":
    main()
