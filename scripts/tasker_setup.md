# Tasker + AutoInput로 폰 안에서만 신용액 자동 조회하기

PC/케이블 없이, 폰 하나로 "삼성증권 POP 앱 실행 → PIN 로그인 → 신용현황
이동 → 신용액 읽기 → 기록"까지 수행하는 방법입니다. 화면을 캡처해서
OCR로 읽는 대신, **접근성 서비스로 화면의 글자 요소를 직접 읽기** 때문에
글자 인식 오류가 없습니다.

## 설치할 것

1. **Tasker** (Play 스토어, 유료) — 자동화 엔진
2. **AutoInput** (Play 스토어, 유료, Tasker 플러그인) — 화면 요소 탭/읽기
3. 두 앱 모두 설치 후 **손쉬운 사용(접근성) 권한**을 켜야 합니다.
   - 설정 → 손쉬운 사용(접근성) → Tasker, AutoInput 둘 다 켜기

## 큰 그림

Tasker에서 "신용액 갱신"이라는 Task(작업)를 하나 만들고, 그 안에
아래 순서로 Action(동작)을 쌓습니다. 각 Action은 Tasker 앱 안에서
`+` 버튼으로 추가합니다.

앱을 실행하면 자동으로 잔고 화면으로 가면서 곧바로 비밀번호 인증
화면이 뜨므로, "잔고" 탭이나 패턴 취소 단계는 필요 없습니다. 이 인증
화면은 보안키패드(글자별 버튼을 탭하는 방식)라서, 비밀번호는 `Set Text`
가 아니라 **글자마다 Click 액션을 하나씩** 만들어 순서대로 눌러야
합니다. 자세한 내용은 아래 "3) 비밀번호 입력" 참고.

| 순서 | 동작 | Tasker Action |
|---|---|---|
| 1 | 삼성증권 POP 앱 실행 | `App > Load App` |
| 2 | 1~2초 대기 (인증 화면 뜰 시간) | `Task > Wait` |
| 3 | 비밀번호 글자 수만큼 버튼 Click (글자마다 반복) | `Plugin > AutoInput > Action`, Text: 해당 글자, Type: `Click` |
| 4 | "확인/로그인" 탭 | `Plugin > AutoInput > Action`, Text: `확인` (실제 버튼 문구로 수정), Type: `Click` |
| 5 | 대기 | `Task > Wait` (0.5~1초) |
| 6 | 신용현황 메뉴로 이동 | `Plugin > AutoInput > Action` (텍스트로 탭: "신용현황" 등) |
| 7 | 신용액 텍스트 요소 읽기 | `Plugin > AutoInput > Query` → 결과를 변수 `%credit_amount` 에 저장 |
| 8 | 결과 기록 | `File > Write File` (로컬 csv) 또는 `Net > HTTP Request` (구글시트 등으로 전송) |

> 글자별 Click 방식은 비밀번호 순서가 Task 설정 화면에 그대로 노출되는
> 구조라, `Set Text` 방식만큼 값을 숨기기는 어렵습니다. 폰 화면 잠금을
> 걸어두고, 이 Task를 다른 사람이 볼 수 없게 관리하세요.

이 Task를 다 만든 뒤, 아래 중 하나로 "트리거"를 답니다.

- **홈 화면 버튼**: Tasker의 "Task 위젯"을 홈 화면에 추가하면, 탭 한 번에 실행됩니다.
- **정해진 시간마다 자동 실행**: Tasker의 Profile → Time 을 만들어 이 Task를 연결합니다.

## 세부 단계

### 1) 앱 실행 (Action 1)

`+` → `App` → `Load App` → 삼성증권 POP 선택.

### 2) 대기 (Action 2)

`+` → `Task` → `Wait` → 1.5초 정도.

### 3) 비밀번호 입력 (Action 3~)

앱을 켜면 곧바로 비밀번호 인증 화면이 뜹니다. 이 화면은 일반 텍스트
입력칸이 아니라 **보안키패드**(글자별 버튼을 화면에 그려서 탭하게 하는
방식, 매번 배열이 랜덤일 수 있음)이므로, `Set Text`가 아니라 **비밀번호
글자 수만큼 Click 액션을 순서대로** 만들어야 합니다. 배열이 랜덤이어도
"지금 화면에 보이는 그 글자" 버튼을 찾아 누르는 방식이라 정상 동작할
가능성이 높습니다.

예를 들어 비밀번호가 4글자(`1`,`a`,`2`,`b`)라면:

1. `Plugin > AutoInput > Action` — Text: `1`, Type: `Click`
2. `Task > Wait` 0.2~0.3초
3. `Plugin > AutoInput > Action` — Text: `a`, Type: `Click`
4. `Task > Wait` 0.2~0.3초
5. `Plugin > AutoInput > Action` — Text: `2`, Type: `Click`
6. `Task > Wait` 0.2~0.3초
7. `Plugin > AutoInput > Action` — Text: `b`, Type: `Click`
8. `Task > Wait` 0.2~0.3초
9. `Plugin > AutoInput > Action` — Text: `확인` (실제 로그인 버튼
   문구로 수정), Type: `Click`
10. `Task > Wait` 0.5~1초

실제 비밀번호 글자 수/문자에 맞춰 1~8번을 늘리거나 줄이면 됩니다.
(참고: 대문자/소문자, 특수문자 키패드 전환이 필요한 비밀번호면 키패드
전환 버튼을 누르는 Click 액션도 중간에 추가해야 할 수 있습니다.)

### 4) 신용현황 메뉴 이동 (Action 5)

`Plugin > AutoInput > Action` → Match Text: `신용현황` (실제 메뉴
문구에 맞게 수정) → Click.
메뉴 depth가 여러 단계면(예: 하단 탭 → 자산 → 신용현황), 이 Action을
단계별로 여러 개 이어 붙이면 됩니다. 중간중간 `Wait` 0.5~1초씩 넣어야
화면 전환 중 탭이 씹히지 않습니다.

### 6) 신용액 값 읽기 (Action 6)

같은 방식으로 Query를 한 번 더 실행해서, 신용액 화면의 요소 목록을
가져온 뒤 "신용" 문구 근처의 숫자 텍스트 요소를 찾습니다. AutoInput은
찾은 요소들의 `text` 값을 변수로 넘겨주므로, 그 중 신용액에 해당하는
값을 `%credit_amount` 변수에 옮겨 담습니다 (`Variable > Variable Set`
또는 Query의 결과 변수를 그대로 사용).

### 7) 기록 (Action 7)

가장 간단한 방법은 로컬 파일에 이어쓰기:

`+` → `File` → `Write File`
- File: `credit_balance_log.csv`
- Text: `%TIMES,%credit_amount` (Tasker 내장 변수 `%TIMES`가 현재 시각)
- Append 옵션 켜기

나중에 그래프나 다른 앱에서 보고 싶으면, `Write File` 대신
`Net > HTTP Request`로 구글 스프레드시트(Apps Script 웹훅) 등에
전송하도록 바꿀 수 있습니다.

## 실행 트리거 달기

- **수동 실행(버튼)**: 홈 화면 길게 눌러 위젯 추가 → Tasker → Task →
  "신용액 갱신" 선택. 이후로는 그 아이콘 한 번 탭으로 전체 과정이 자동
  실행됩니다. (지금 원하시는 "필요할 때 수동 실행"에 맞는 방식입니다.)
- **주기적 자동 실행**을 나중에 원하시면, Tasker Profile을 하나 만들어
  Time 조건(예: 매일 오전 9시)에 이 Task를 연결하면 됩니다.

## 막히는 지점

이 가이드에서 실제 버튼/문구 이름(예: "신용현황"이 맞는지, 메뉴 depth가
몇 단계인지, PIN 버튼의 id)은 앱을 직접 봐야 정확히 알 수 있어서
placeholder로 남겨뒀습니다. AutoInput Query로 스캔한 화면 요소 목록
스크린샷을 캡처해서 보내주시면, 어떤 값을 넣어야 하는지 구체적으로
짚어드릴게요.
