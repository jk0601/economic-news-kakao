# API 키 발급 방법

## 1. 네이버 뉴스 API

**👉 https://developers.naver.com**

### 순서

**① 네이버 로그인 후 접속**

- 상단 메뉴 → **"Application" → "애플리케이션 등록"** 클릭

**② 애플리케이션 정보 입력**

```
애플리케이션 이름: 경제뉴스봇 (자유롭게)
사용 API: "검색" 체크 ✅
환경 추가: WEB 설정 → URL: http://localhost
```

**③ 등록 완료 후**

- **Client ID** → `NAVER_CLIENT_ID`
- **Client Secret** → `NAVER_CLIENT_SECRET`

> 💡 무료 / 하루 25,000회 / 별도 심사 없음

--- ===================================================================

## 2. NewsAPI 키

**👉 https://newsapi.org**

### 순서

**① 회원가입**

- 우측 상단 **"Get API Key"** 클릭
- 이름 / 이메일 / 비밀번호 입력 후 가입

**② 이메일 인증**

- 가입 후 인증 메일 → 링크 클릭

**③ 대시보드에서 키 확인**

- 로그인 → **"Your API key"** 바로 표시됨
- 이 값 → `NEWSAPI_KEY`

> 💡 무료 플랜 월 1,000회 / 개인 프로젝트 충분

--- ===================================================================

## 3. Notion API 키 + Database ID

**👉 https://www.notion.so/my-integrations**

### 3-1. Integration Token 발급

**① 접속 후 로그인**

**② "New integration" 클릭**

```
이름: 경제뉴스봇
Associated workspace: 내 워크스페이스 선택
Type: Internal
```

**"Submit"** 클릭

**③ 토큰 복사**

- **"Internal Integration Secret"** 옆 **"Show"** → 복사
- 이 값 → `NOTION_TOKEN`

---

### 3-2. Notion 데이터베이스 생성 + ID 발급

**① Notion 앱/웹에서 새 페이지 생성**

- 좌측 사이드바 **"+ New page"**
- 제목: `📰 경제 뉴스 브리핑`

**② 데이터베이스 삽입**

- 페이지 본문에서 `/` 입력 → **"Table"** 선택 → **"New database"**

**③ 속성(컬럼) 설정**

```
기본 생성된 "Name" 컬럼 → 그대로 사용 (title 역할)
"+" 버튼으로 새 속성 추가:
  - 속성명: 날짜
  - 타입: Date
```

**④ Integration 연결** ← 이 단계 빠뜨리면 저장 안 됨!

- 페이지 우측 상단 **"..."** 클릭
- **"Connections"** → **"경제뉴스봇"** 검색 후 연결 ✅

**⑤ Database ID 복사**

- 브라우저 주소창 URL 확인:

```
https://www.notion.so/경제뉴스봇-[여기가-DATABASE-ID]?v=xxxxx
```

- `?v=` 앞의 **32자리 문자열** 복사
- 예: `1a2b3c4d5e6f7890abcd1234567890ef`
- 이 값 → `NOTION_DATABASE_ID`


--- ===================================================================

## 4. OpenAI API 키

## STEP 1. 플랫폼 접속 및 회원가입

**👉 https://platform.openai.com 접속**

사이트에 들어가면 **"Sign up"** 또는 **"Get started"** 버튼이 보입니다. 이메일 주소를 직접 입력해도 되고, Google이나 Microsoft 계정으로 연동해서 더 간편하게 가입할 수 있습니다.

```
가입 방법 선택:
  ① 이메일 + 비밀번호로 직접 가입
  ② Google 계정으로 소셜 로그인  ← 가장 간편
  ③ Microsoft 계정으로 소셜 로그인
```

---

## STEP 2. 전화번호 인증

API 키 발급을 위해 상단 **"Start verification"** 버튼을 클릭해 전화번호 실명인증을 진행합니다. 문자메시지로 발급된 확인 코드 6자리를 확인하고 입력합니다.

> ⚠️ **한국 번호 사용 가능** — +82 선택 후 010 번호 앞 0 제거하고 입력 예: 010-1234-5678 → **10-1234-5678**

---

## STEP 3. 결제 수단 등록 및 크레딧 충전 ← 필수!

좌측 Settings → **Billing** → **"Add payment details"** 버튼을 클릭해서 유료 요금제 신청 및 결제수단을 등록합니다. 개인 또는 회사 소속으로 신청할지 선택한 뒤, 신용카드 번호와 결제 청구 주소 정보를 입력합니다.

### 충전 금액 설정

**Initial credit purchase**에 최소 **5달러** 입력 → **"Yes, automatically recharge my card..."** 왼쪽 체크 표시를 **해제** → Continue 버튼 클릭.

> 💡 자동 충전 체크 해제를 권장합니다 — 예상치 못한 과금 방지

|충전 금액|한화 약|뉴스봇 사용 가능 기간|
|---|---|---|
|$5|약 7,000원|약 **5,000일치** (13년!)|
|$10|약 14,000원|넉넉하게 시작 가능|

---

## STEP 4. API 키 생성

**👉 https://platform.openai.com/api-keys 바로 접속**

**"Create new secret key"** 버튼을 클릭합니다. 팝업 창에 적당한 이름을 넣고 **"Create secret key"** 버튼을 클릭합니다.

```
Name (키 이름): news-bot       ← 나중에 구분하기 위해 입력
Project       : Default project
Permission    : All           ← 기본값 그대로
```

---

## STEP 5. 키 복사 및 보관 ← 가장 중요!

키가 발급되는 순간이 가장 중요합니다. 화면에 보이는 Secret key를 **바로 복사해서 메모장이나 안전한 곳에 저장**해 두세요. 이 창을 닫으면 다시는 전체 키 내용을 확인할 수 없기 때문입니다.

발급된 키 형태:

```
sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> ✅ 복사 완료 후 → **"Done"** 버튼 클릭

---

## STEP 6. config.py에 키 입력

```python
# config.py
OPENAI_API_KEY = "sk-proj-xxxxxxxxxxxxxxxx"  # 방금 복사한 키 붙여넣기
```

---

## STEP 7. 연결 테스트 (선택)

```bash
# 터미널에서 바로 테스트
pip install openai

python -c "
from openai import OpenAI
client = OpenAI(api_key='sk-proj-여기에키입력')
res = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[{'role':'user','content':'안녕! 한국어로 대답해줘'}]
)
print(res.choices[0].message.content)
"
```

정상이면 한국어 응답이 출력됩니다! ✅

---

## ⚠️ 보안 주의사항 요약

API 키가 유출될 경우 제3자가 무단으로 키를 사용하여 과금이 청구될 수 있으니, API Key는 절대 외부에 유출되거나 노출되지 않도록 조심해야 합니다. 특히, 코드 안에 키 값이 노출된 상태에서 코드를 GitHub에 업로드하면 키가 바로 유출될 수 있으니 각별히 주의하세요.

보안을 위해 OpenAI는 인터넷상에 공개된 API Key들은 자동으로 비활성화 처리합니다.

```
❌ 절대 하지 말 것:
  - config.py를 GitHub에 올리기
  - 카카오톡/슬랙으로 키 공유
  - 코드에 키 직접 하드코딩 후 공개

✅ 안전하게 관리:
  - config.py는 로컬에만 보관
  - 메모장 등 오프라인에 백업
  - 유출 의심 시 즉시 삭제 후 재발급
```

---

## ✅ 전체 발급 체크리스트

```
□ platform.openai.com 회원가입
□ 전화번호 인증 완료
□ 결제 카드 등록 + $5 충전
□ API Keys 메뉴 → Create new secret key
□ 키 즉시 복사 → 메모장 저장
□ config.py에 붙여넣기
□ python 테스트 실행 확인
```

--- ========================================================================

## 5. config.py 최종 완성

모든 키를 발급받은 후 아래처럼 입력하세요:

```python
# config.py

NAVER_CLIENT_ID     = "abc12345"             # 네이버 Client ID
NAVER_CLIENT_SECRET = "xYz9876secret"        # 네이버 Client Secret
NEWSAPI_KEY         = "abcd1234efgh5678"     # NewsAPI 키
ANTHROPIC_API_KEY   = "sk-ant-api03-xxxxx"  # Anthropic 키 (sk-ant-로 시작)
NOTION_TOKEN        = "secret_xxxxxxxxxxx"  # Notion 토큰 (secret_으로 시작)
NOTION_DATABASE_ID  = "1a2b3c4d5e6f7890..."# Notion DB ID (32자리)
```

---

## ✅ 발급 체크리스트

```
□ 네이버 개발자 센터 → Client ID / Secret 복사
□ NewsAPI.org → API Key 복사
□ Anthropic Console → 카드 등록 + API Key 복사
□ Notion → Integration 생성 + Token 복사
□ Notion → 데이터베이스 생성 + Integration 연결 + DB ID 복사
□ config.py에 모두 입력 완료
```

---