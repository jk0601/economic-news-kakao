# 카카오 REST API 발급 및 설정 방법

> 경제 뉴스 브리핑을 **카카오톡 나에게 보내기**로 전송하려면 아래 과정이 필요합니다.

---

## 개요

카카오톡 "나에게 쓰기"에 메시지를 보내려면 다음이 필요합니다:

| 구분 | 설명 |
|------|------|
| **앱 등록** | 카카오 개발자 콘솔에서 애플리케이션 생성 |
| **카카오 로그인** | 앱에 카카오 로그인 활성화 |
| **동의 항목** | `talk_message` (카카오톡 메시지 전송) 설정 |
| **Access Token** | OAuth 2.0 인증을 통해 발급 (REST API 기준 유효 6시간) |
| **Refresh Token** | Access Token 만료 시 갱신용 (유효 2개월) |

---

## 1. 카카오 개발자 앱 등록

**👉 https://developers.kakao.com/console/app**

### 1-1. 애플리케이션 생성

**① 카카오 계정으로 로그인** 후 "애플리케이션 추가하기" 클릭

**② 앱 정보 입력**

```
앱 이름: 경제뉴스봇 (원하는 이름)
사업자명: 개인 또는 본인 이름
```

**③ 생성 완료 후** → 앱 선택 → **앱 키** 섹션 확인

---

### 1-2. REST API 키 및 Client Secret 확인

**① [앱] → [앱 키]** 메뉴 이동

**② REST API 키 복사**
- **REST API 키** → `KAKAO_REST_API_KEY` (숫자로 된 긴 문자열)

**③ Client Secret 확인** (토큰 발급 시 사용)

- REST API 키 행에서 **Client Secret** 항목 확인
- 기본적으로 **ON** 상태이며, 토큰 발급 시 필수로 포함해야 함
- **"코드"** 또는 **"발급"** 버튼 클릭 → `KAKAO_CLIENT_SECRET` 복사

---

### 1-3. Redirect URI 등록 (필수)

카카오 로그인 후 인증 코드를 받을 주소를 등록해야 합니다.

**① [앱] → [플랫폼] → [웹]** 메뉴 이동

- 플랫폼이 없다면 "웹" 플랫폼 추가

**② Redirect URI 등록**

```
http://localhost:8080/callback
```

또는 로컬 테스트용:

```
http://127.0.0.1:8080/callback
```

> ⚠️ 실제 Redirect URI는 앱 등록 시 입력한 값과 **완전히 동일**해야 합니다.  
> `http` / `https`, 포트 번호, 끝 `/` 유무까지 일치해야 합니다.

---

## 2. 카카오 로그인 활성화

**👉 [앱] → [제품 설정] → [카카오 로그인]**

**① 상태를 "ON"으로 변경**

- OFF일 경우 `KOE004` 오류 발생

---

## 3. 동의 항목 설정 (카카오톡 메시지 전송)

**나에게 보내기** 기능을 쓰려면 **"카카오톡 메시지 전송"** 동의가 필요합니다.

**👉 [앱] → [제품 설정] → [카카오 로그인] → [동의항목]**

**① 접근권한 동의항목** 탭 선택

**② "카카오톡 메시지 전송" (`talk_message`)** 찾기

- **설정** 클릭 → **사용** 체크
- **동의 목적**: "경제 뉴스 브리핑을 카카오톡으로 받기" 등 입력
- **저장**

> 💡 `talk_message`는 **접근권한 동의항목**에 있습니다.  
> 개인정보 항목이 아닙니다.

---

## 4. Access Token 발급 절차 (OAuth 2.0)

### 전체 흐름

```
1) 사용자가 카카오 로그인 URL 접속
2) 카카오 계정 로그인 + 동의 화면에서 "동의하고 계속하기"
3) Redirect URI로 code(인증 코드) 전달
4) code로 토큰 발급 API 호출
5) access_token, refresh_token 수신
```

---

### 4-1. 1단계: 인증 코드 요청 URL로 접속

브라우저에서 아래 URL을 열어주세요. (치환 후 사용)

```
https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=${REST_API_KEY}&redirect_uri=${REDIRECT_URI}&scope=talk_message
```

**치환 예시:**
```
https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=1234567890abcdef&redirect_uri=http://localhost:8080/callback&scope=talk_message
```

| 파라미터 | 설명 |
|----------|------|
| `client_id` | REST API 키 |
| `redirect_uri` | 앱에 등록한 Redirect URI (URL 인코딩) |
| `scope` | `talk_message` — 카카오톡 메시지 전송 권한 |

**② 카카오 로그인** → **동의하고 계속하기** 클릭

**③ 리다이렉트된 URL에서 `code` 확인**

예:
```
http://localhost:8080/callback?code=XXXXXXXXXXXXXXXX
```

`?code=` 뒤의 문자열이 **인증 코드(Authorization Code)**입니다. 이 코드는 **한 번만** 사용 가능하고, **몇 분 안에 만료**됩니다.

---

### 4-2. 2단계: 토큰 발급 API 호출

받은 `code`로 Access Token을 발급받습니다.

**엔드포인트:**
```
POST https://kauth.kakao.com/oauth/token
```

**헤더:**
```
Content-Type: application/x-www-form-urlencoded;charset=utf-8
```

**Body (form-urlencoded):**

| 파라미터 | 값 |
|----------|-----|
| grant_type | `authorization_code` |
| client_id | REST API 키 |
| redirect_uri | 인증 코드 요청 시 사용한 Redirect URI와 동일 |
| code | 위에서 받은 인증 코드 |
| client_secret | Client Secret (설정이 ON일 때 필수) |

**cURL 예시:**
```bash
curl -X POST "https://kauth.kakao.com/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded;charset=utf-8" \
  -d "grant_type=authorization_code" \
  -d "client_id=YOUR_REST_API_KEY" \
  -d "redirect_uri=http://localhost:8080/callback" \
  -d "code=YOUR_AUTHORIZATION_CODE" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

**응답 예시:**
```json
{
  "token_type": "bearer",
  "access_token": "abc123...",
  "expires_in": 21599,
  "refresh_token": "xyz789...",
  "refresh_token_expires_in": 5184000,
  "scope": "talk_message"
}
```

- `access_token` → API 호출 시 사용 (REST API 기준 약 6시간 유효)
- `refresh_token` → Access Token 만료 시 갱신용 (2개월 유효)

---

### 4-3. 3단계: Refresh Token으로 Access Token 갱신

**한 줄 요약:** 이미 **4-2 응답에서 저장해 둔 `refresh_token`** 과 REST API 키·Client Secret을 넣어 **같은 토큰 URL**에 `POST`하면, 카카오가 **새 `access_token`**(및 경우에 따라 새 `refresh_token`)을 JSON으로 돌려줍니다. 그중 `access_token` 값을 `config.py`의 `KAKAO_ACCESS_TOKEN`에 다시 넣으면 됩니다.

#### 전제 조건

- **4-2에서 한 번이라도** 토큰 발급을 성공했고, 그때 받은 **`refresh_token` 문자열**을 메모장 등에 저장해 두었을 것.
- `refresh_token`이 없거나 만료(대략 2개월·카카오 정책 따름)면 이 방법으로는 갱신할 수 없습니다. 그때는 **4-1부터 다시** 로그인해서 `code` → 4-2로 새 토큰 세트를 받아야 합니다.

#### 무엇을 “받는” 건가요?

| 용어 | 의미 |
|------|------|
| 요청에 넣는 것 | 예전에 받아 둔 **`refresh_token`** (갱신용 비밀번호 같은 값) |
| 응답으로 오는 것 | **새 `access_token`** (API 호출에 쓰는 값, 다시 약 6시간 유효) |
| 가끔 같이 오는 것 | 새 **`refresh_token`** — 응답에 있으면 그 값으로 기존 refresh를 **교체 저장**하는 것이 안전합니다. |

즉, “refresh access_token을 받는다”기보다 **“refresh_token을 제시하고, 서버가 새 access_token을 발급한다”**고 이해하면 됩니다.

#### 직접 호출하는 방법 (cURL)

1. 아래 예시에서 `YOUR_REST_API_KEY`, `YOUR_REFRESH_TOKEN`, `YOUR_CLIENT_SECRET`을 **본인 값으로만** 바꿉니다. (따옴표 안에 그대로 붙여넣기. 값에 `&` 등 특수문자가 있으면 URL 인코딩이 필요할 수 있습니다.)
2. **터미널(CMD, PowerShell, macOS 터미널 등)**에서 한 번에 실행합니다.
3. 화면에 **JSON 한 덩어리**가 출력되면 성공입니다.

**엔드포인트:**
```
POST https://kauth.kakao.com/oauth/token
```

**Body (form-urlencoded):**

| 파라미터 | 값 |
|----------|-----|
| grant_type | `refresh_token` |
| client_id | REST API 키 |
| refresh_token | 4-2에서 저장해 둔 Refresh Token |
| client_secret | Client Secret |

**cURL 예시 (Git Bash / macOS / Linux):**
```bash
curl -X POST "https://kauth.kakao.com/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded;charset=utf-8" \
  -d "grant_type=refresh_token" \
  -d "client_id=YOUR_REST_API_KEY" \
  -d "refresh_token=YOUR_REFRESH_TOKEN" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

**Windows PowerShell에서 `curl`이 이상하면** `curl.exe`로 실행해 보세요:
```powershell
curl.exe -X POST "https://kauth.kakao.com/oauth/token" `
  -H "Content-Type: application/x-www-form-urlencoded;charset=utf-8" `
  -d "grant_type=refresh_token" `
  -d "client_id=YOUR_REST_API_KEY" `
  -d "refresh_token=YOUR_REFRESH_TOKEN" `
  -d "client_secret=YOUR_CLIENT_SECRET"
```

**응답 예시 (발췌):**
```json
{
  "token_type": "bearer",
  "access_token": "새로_받은_액세스_토큰...",
  "expires_in": 21599,
  "refresh_token": "새로_줄_수도_있는_리프레시...",
  "refresh_token_expires_in": 5184000
}
```

**그다음 할 일**

1. JSON에서 **`access_token`** 값만 복사 → `config.py`의 `KAKAO_ACCESS_TOKEN`에 붙여넣기.
2. **`refresh_token` 키가 응답에 있으면** 그 값도 복사 → `KAKAO_REFRESH_TOKEN`에 덮어쓰기.
3. 저장 후 `python main.py` 또는 `python kakao_sender.py`로 전송이 되는지 확인.

#### 이 프로젝트에서는 (수동 cURL 없이)

`kakao_sender.py`의 `_refresh_access_token()`이 **위와 동일한 POST**를 코드로 호출합니다. `config.py`에 **`KAKAO_REFRESH_TOKEN`(과 REST 키·시크릿)**만 올바르게 있으면, **access가 만료된 뒤에도** `main.py` / `kakao_sender.py` 실행 시 자동으로 새 access를 받아 다시 보내기를 시도합니다.  
수동 cURL은 **자동 갱신이 실패할 때** 원인 확인용으로 쓰면 됩니다.

---

## 5. 나에게 메시지 보내기 API

### 5-1. 기본 정보

| 항목 | 내용 |
|------|------|
| Method | `POST` |
| URL | `https://kapi.kakao.com/v2/api/talk/memo/default/send` |
| Authorization | `Bearer ${ACCESS_TOKEN}` |
| Content-Type | `application/x-www-form-urlencoded;charset=utf-8` |

### 5-2. Text 템플릿 (텍스트 메시지)

뉴스 요약은 **Text** 타입이 적합합니다. (최대 200자)

**Body (form-urlencoded):**

| 파라미터 | 설명 |
|----------|------|
| template_object | JSON 문자열 (아래 형식) |

**template_object (Text 타입) 예시:**
```json
{
  "object_type": "text",
  "text": "오늘의 경제 뉴스 핵심 요약...",
  "link": {
    "web_url": "https://example.com",
    "mobile_web_url": "https://example.com"
  },
  "button_title": "자세히 보기"
}
```

| 필드 | 필수 | 설명 |
|------|------|------|
| object_type | O | `"text"` |
| text | O | 본문 (최대 200자) |
| link | X | 링크 정보 |
| button_title | X | 버튼 문구 |

> ⚠️ **제한**: Text 템플릿의 `text` 필드는 **최대 200자**입니다.  
> 뉴스 요약이 200자를 넘으면 **Feed** 또는 **List** 템플릿을 사용하거나, 여러 메시지로 나눠 보내야 합니다.

### 5-3. cURL 예시

```bash
curl -X POST "https://kapi.kakao.com/v2/api/talk/memo/default/send" \
  -H "Content-Type: application/x-www-form-urlencoded;charset=utf-8" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  --data-urlencode 'template_object={"object_type":"text","text":"경제 뉴스 브리핑 테스트입니다."}'
```

**성공 응답:**
```json
{
  "result_code": 0
}
```

### 5-4. Feed / List 템플릿 (200자 초과 시)

긴 내용은 **Feed** 또는 **List** 템플릿을 사용합니다.  
공식 문서: https://developers.kakao.com/docs/latest/en/message-template/default

---

## 6. config.py에 넣을 값

```python
# config.py (카카오 관련)

KAKAO_REST_API_KEY   = "YOUR_REST_API_KEY"      # 앱 키 > REST API 키
KAKAO_CLIENT_SECRET  = "YOUR_CLIENT_SECRET"     # REST API > Client secret
KAKAO_REDIRECT_URI   = "http://localhost:8080/callback"  # 등록한 Redirect URI

# 토큰 (4단계에서 발급 후 여기에 저장)
KAKAO_ACCESS_TOKEN   = "YOUR_ACCESS_TOKEN"      # API 호출 시 사용
KAKAO_REFRESH_TOKEN  = "YOUR_REFRESH_TOKEN"     # Access Token 갱신 시 사용
```

---

## 7. 로컬에서 인증 코드 받기 (간단한 방법)

Redirect URI로 `http://localhost:8080/callback`을 쓸 경우,  
인증 코드를 받으려면 **로컬에서 8080 포트로 요청을 받을 서버**가 필요합니다.

### Python으로 간단한 콜백 서버 예시

```python
# get_kakao_token.py (한 번만 실행해서 토큰 발급용)
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests

REST_API_KEY = "YOUR_REST_API_KEY"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8080/callback"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/callback":
            qs = parse_qs(parsed.query)
            code = qs.get("code", [None])[0]
            if code:
                # 토큰 발급
                resp = requests.post(
                    "https://kauth.kakao.com/oauth/token",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "grant_type": "authorization_code",
                        "client_id": REST_API_KEY,
                        "redirect_uri": REDIRECT_URI,
                        "code": code,
                        "client_secret": CLIENT_SECRET
                    }
                )
                result = resp.json()
                print("access_token:", result.get("access_token"))
                print("refresh_token:", result.get("refresh_token"))

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK. Check console for tokens.")

    def log_message(self, format, *args):
        pass

print("1. 브라우저에서 아래 URL 접속:")
print(f"https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&scope=talk_message")
print("\n2. 로그인 후 동의하고 계속하기 클릭")
print("3. 콘솔에서 access_token, refresh_token 확인\n")

HTTPServer(("", 8080), Handler).serve_forever()
```

실행 후 브라우저에서 인증 URL 접속 → 동의 → 콘솔에 토큰 출력.

---

## 8. 발급 체크리스트

```
□ developers.kakao.com 에서 앱 생성
□ REST API 키, Client Secret 복사
□ Redirect URI 등록 (웹 플랫폼)
□ 카카오 로그인 상태 ON
□ 동의항목: talk_message (카카오톡 메시지 전송) 활성화
□ 인증 코드 발급 URL로 접속 후 로그인/동의
□ code로 토큰 발급 API 호출
□ access_token, refresh_token 저장
□ config.py에 KAKAO_* 값 입력
```

---

## 9. 참고 문서

| 항목 | URL |
|------|-----|
| 카카오 개발자 콘솔 | https://developers.kakao.com/console/app |
| 카카오 로그인 REST API | https://developers.kakao.com/docs/latest/en/kakaologin/rest-api |
| 나에게 메시지 보내기 | https://developers.kakao.com/docs/latest/en/kakaotalk-message/rest-api |
| 기본 템플릿 | https://developers.kakao.com/docs/latest/en/message-template/default |
| REST API 테스트 | 개발자 콘솔 > [도구] > [REST API 테스트] |

---

## 10. 주의사항

### 토큰 유효기간

- **Access Token**: REST API 사용 시 약 **6시간**
- **Refresh Token**: **2개월** (갱신 시 연장)
- 매일 뉴스 브리핑을 보내려면 **Refresh Token으로 Access Token을 주기적으로 갱신**하는 로직이 필요합니다.

### 메시지 길이 제한

- Text: 최대 **200자**
- 200자 초과 시 Feed/List 템플릿 사용 또는 여러 메시지로 분할

### 보안

- `config.py`는 `.gitignore`에 추가
- Access Token, Refresh Token, Client Secret은 외부에 노출하지 않기
