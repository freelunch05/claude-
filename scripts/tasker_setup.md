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

| 순서 | 동작 | Tasker Action |
|---|---|---|
| 1 | 삼성증권 POP 앱 실행 | `App > Load App` |
| 2 | 1~2초 대기 (앱 켜질 시간) | `Task > Wait` |
| 3 | 로그인 화면인지 확인 | `Plugin > AutoInput > Query` (텍스트/id로 존재 확인) |
| 4 | (로그인 화면이면) PIN 숫자 버튼 순서대로 탭 | `Plugin > AutoInput > Action` 반복, 또는 좌표 `Tap` |
| 5 | 신용현황 메뉴로 이동 | `Plugin > AutoInput > Action` (텍스트로 탭: "신용현황" 등) |
| 6 | 신용액 텍스트 요소 읽기 | `Plugin > AutoInput > Query` → 결과를 변수 `%credit_amount` 에 저장 |
| 7 | 결과 기록 | `File > Write File` (로컬 csv) 또는 `Net > HTTP Request` (구글시트 등으로 전송) |

이 Task를 다 만든 뒤, 아래 중 하나로 "트리거"를 답니다.

- **홈 화면 버튼**: Tasker의 "Task 위젯"을 홈 화면에 추가하면, 탭 한 번에 실행됩니다.
- **정해진 시간마다 자동 실행**: Tasker의 Profile → Time 을 만들어 이 Task를 연결합니다.

## 세부 단계

### 1) 앱 실행 (Action 1)

`+` → `App` → `Load App` → 삼성증권 POP 선택.

### 2) 대기 (Action 2)

`+` → `Task` → `Wait` → 1.5초 정도.

### 3) 로그인 화면인지 확인 + PIN 입력 (Action 3~4)

AutoInput의 `Query` action으로 로그인 화면에만 있는 요소(예: 간편비밀번호
입력 안내 문구)가 화면에 있는지 확인합니다. 방법:

1. `+` → `Plugin` → `AutoInput` → `Query`
2. Query 화면에서 우측 상단 돋보기(스캔) 버튼을 눌러 **지금 폰에 떠 있는
   화면의 요소 목록**을 가져옵니다. (이때 실제로 폰에 로그인 화면을
   띄워둔 상태여야 합니다.)
3. 목록에서 PIN 숫자 버튼(0~9)들의 `id`나 `text`를 확인해 적어둡니다.
4. Query 결과가 있으면(`%ai_result` 등에 값이 들어옴) `If` 조건으로
   분기하고, PIN 자리수만큼 `Plugin > AutoInput > Action`으로 해당 숫자
   버튼을 순서대로 탭하게 만듭니다. (`Action` 타입에서 "Text" 또는
   "View Id"로 대상 지정 후 `Click`)

> PIN 자체는 화면에 노출되면 안 되니, Tasker 변수에 저장할 때는
> `%credit_pin` 같은 이름으로 만들고, 이 변수는 Tasker 앱 내
> "Configuration" 화면에서만 입력해두고 Task 안에서는 값을 직접
> 노출하지 않도록 합니다. (완전한 암호화는 아니지만, 캡처/스크린샷에
> 값이 노출되지 않게는 해줍니다.)

### 4) 신용현황 메뉴 이동 (Action 5)

`Plugin > AutoInput > Action` → Match Text: `신용현황` (실제 메뉴
문구에 맞게 수정) → Click.
메뉴 depth가 여러 단계면(예: 하단 탭 → 자산 → 신용현황), 이 Action을
단계별로 여러 개 이어 붙이면 됩니다. 중간중간 `Wait` 0.5~1초씩 넣어야
화면 전환 중 탭이 씹히지 않습니다.

### 5) 신용액 값 읽기 (Action 6)

같은 방식으로 Query를 한 번 더 실행해서, 신용액 화면의 요소 목록을
가져온 뒤 "신용" 문구 근처의 숫자 텍스트 요소를 찾습니다. AutoInput은
찾은 요소들의 `text` 값을 변수로 넘겨주므로, 그 중 신용액에 해당하는
값을 `%credit_amount` 변수에 옮겨 담습니다 (`Variable > Variable Set`
또는 Query의 결과 변수를 그대로 사용).

### 6) 기록 (Action 7)

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
