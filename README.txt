================================================================================
                    경제 뉴스 브리핑 봇 - 사용 설명서
                 Economic News Briefing Bot for Beginners
================================================================================

■ 이 봇이 하는 일
--------------------------------------------------------------------------------
이 프로그램은 아래 순서대로 자동으로 경제 뉴스를 수집하고 정리합니다:

  1) 국내·글로벌 경제 뉴스 수집 (네이버 API + NewsAPI)
  2) 주요 시장 지표 수집 (S&P500, 나스닥, 엔비디아, 환율, 원유 등)
  3) OpenAI GPT-4o-mini로 뉴스 요약 및 브리핑 작성
  4) Notion 데이터베이스에 자동 저장
  5) 브리핑 내용을 docs/ 폴더에 HTML 파일로 저장 (로컬·GitHub Pages·iframe 연동용)

실행하면 Notion에 "오늘의 경제 뉴스 브리핑" 페이지가 하나 생성되고,
docs/ 에 news_YYYYMMDD.html 과 briefing.html 이 생성·갱신됩니다.


■ 사전 준비 (필수)
--------------------------------------------------------------------------------
  □ Python 3.8 이상 설치
  □ 필요한 API 키 5종 발급 (아래 'API 키 발급' 섹션 참고)
  □ Notion 계정


================================================================================
                        처음 설치 및 실행 방법
================================================================================

[1단계] Python 설치 확인
--------------------------------------------------------------------------------
  Windows 명령 프롬프트(CMD) 또는 PowerShell을 열고 다음을 입력하세요:

    python --version

  예: Python 3.11.0 이렇게 뜨면 정상입니다.
  없다면 https://www.python.org/downloads/ 에서 다운로드 후 설치하세요.
  설치 시 "Add Python to PATH"를 반드시 체크하세요.


[2단계] 프로젝트 폴더로 이동
--------------------------------------------------------------------------------
  CMD/PowerShell에서:

    cd d:\j\cursor\economic_news_bot

  (실제 프로젝트가 있는 경로로 바꾸세요.)


[3단계] 가상환경 생성 (선택, 권장)
--------------------------------------------------------------------------------
  같은 폴더에서:

    python -m venv venv

  그 다음, 가상환경 활성화:

    venv\Scripts\activate

  (PowerShell에서 실행 권한 오류가 나면: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser)


[4단계] 패키지 설치
--------------------------------------------------------------------------------
  가상환경이 활성화된 상태에서:

    pip install -r requirements.txt

  설치되는 패키지: openai, requests, yfinance

  (※ py -m pip install --upgrade pip 나오면 upgrade도 한번 실행)

[5단계] config.py 설정 (가장 중요!)
--------------------------------------------------------------------------------
  ① .config.sample.py 파일을 config.py로 복사:

       copy .config.sample.py config.py

     (PowerShell에서는: Copy-Item .config.sample.py config.py)

  ② config.py를 메모장이나 VS Code로 열어서 YOUR_xxx 자리에 실제 API 키를 넣습니다.

  필요한 키:
    - NAVER_CLIENT_ID, NAVER_CLIENT_SECRET  (네이버 개발자 센터)
    - NEWSAPI_KEY                            (newsapi.org)
    - OPENAI_API_KEY                         (platform.openai.com)
    - NOTION_TOKEN, NOTION_DATABASE_ID       (notion.so)

  각 API 키 발급 방법은 "apikey_how.md" 파일에 자세히 적혀 있습니다.


[6단계] 실행
--------------------------------------------------------------------------------
  같은 폴더에서:

    python main.py

  정상 동작 시:
    - 콘솔에 "경제 뉴스 브리핑 시작" 메시지가 보이고
    - 뉴스 수집 → 시장 데이터 수집 → GPT 요약 → HTML 저장(docs/) → Notion 저장 순으로 진행됩니다.
    - 마지막에 "Notion 저장 완료!" 및 페이지 URL이 출력됩니다.
    - docs/ 에 briefing.html, news_YYYYMMDD.html 이 생성됩니다.

  로그는 logs 폴더에 월별로 저장됩니다 (예: logs/2026-03.log).


================================================================================
                        API 키 발급 간단 가이드
================================================================================

자세한 내용은 apikey_how.md를 참고하세요. 여기서는 요약만 적습니다.

  1) 네이버 API
     - https://developers.naver.com
     - Application 등록 → 검색 API 체크 → Client ID, Client Secret 복사

  2) NewsAPI
     - https://newsapi.org
     - 회원가입 → Get API Key → API Key 복사

  3) OpenAI API
     - https://platform.openai.com
     - 회원가입 → 전화번호 인증 → 결제카드 등록 및 $5 충전 → API Keys에서 키 생성

  4) Notion
     - https://www.notion.so/my-integrations
     - New integration 생성 → Token 복사
     - Notion에서 새 페이지에 Table 데이터베이스 만들기
     - 페이지 우측 ... → Connections → 방금 만든 Integration 연결
     - 브라우저 URL에서 ?v= 앞 32자리 = DATABASE_ID


================================================================================
                        프로젝트 파일 구조
================================================================================

  main.py           - 실행 진입점 (여기서 python main.py 실행)
  config.py         - API 키 설정 (직접 생성, .gitignore 권장)
  .config.sample.py - config 예시 (복사해서 config.py 만들기)
  scripts/write_config_from_env.py - CI에서 환경변수로 config.py 생성

  .github/workflows/daily-briefing.yml - 매일 09:00 KST Actions 자동 실행

  html_writer.py    - 브리핑 HTML 생성 (docs/ 저장, GitHub Pages·iframe용)
  docs/             - 브리핑 HTML (briefing.html, news_YYYYMMDD.html), .nojekyll
  news_fetcher.py   - 뉴스 수집 (네이버, NewsAPI)
  market_fetcher.py - 시장 데이터 수집 (yfinance)
  summarizer.py     - GPT로 뉴스 요약
  notion_writer.py  - Notion 저장

  requirements.txt  - pip 패키지 목록
  apikey_how.md     - API 키 발급 상세 가이드
  kakao_api_how.md  - 카카오 REST API(나에게 보내기) 설정 가이드
  .gitignore        - Git 제외 목록 (config.py, venv, logs 등)
  logs/             - 실행 로그 저장 폴더


================================================================================
                        자주 발생하는 오류와 해결
================================================================================

  ■ "ModuleNotFoundError: No module named 'config'"
    → config.py 파일이 없습니다. .config.sample.py를 config.py로 복사하세요.

  ■ "수집된 뉴스가 없습니다. API 키를 확인하세요."
    → NAVER_CLIENT_ID, NEWSAPI_KEY 등이 올바르지 않습니다.
    → config.py의 키 값을 다시 확인하고, apikey_how.md대로 재발급하세요.

  ■ "Notion 저장 실패 (상태코드: 401)" 또는 "403"
    → NOTION_TOKEN이 틀리거나, 해당 페이지에 Integration이 연결되지 않았습니다.
    → Notion 페이지 우측 ... → Connections → Integration 연결을 확인하세요.

  ■ "Notion 저장 실패 (상태코드: 400)"
    → NOTION_DATABASE_ID가 잘못되었거나, DB 속성이 다를 수 있습니다.
    → DB에 "날짜" 속성(Date 타입)이 있어야 합니다. apikey_how.md 참고.

  ■ "openai.AuthenticationError" 또는 API 키 오류
    → OPENAI_API_KEY를 확인하세요. sk-proj- 로 시작하는 형식이어야 합니다.
    → platform.openai.com에서 카드 등록 및 크레딧 충전이 되어 있어야 합니다.


================================================================================
                        GitHub 업로드 시
================================================================================

  저장소 루트에 .gitignore 가 포함되어 있으며, 아래는 커밋되지 않습니다:
    - config.py (API 키)
    - venv/ , __pycache__/ (가상환경·바이트코드)
    - logs/ , *.log (실행 로그)
    - .env 파일, IDE 설정 일부

  처음 clone 한 사람은: copy .config.sample.py config.py 후 키 입력.

  git 저장소를 처음 만든 뒤 예시:
    git init
    git add .
    git status   ← config.py 가 목록에 없어야 정상
    git commit -m "Initial commit"

  이미 config.py 를 한 번이라도 원격에 올렸다면 → 모든 API 키를 재발급하세요.


================================================================================
            GitHub Actions — 매일 한국 시간 09:00 자동 실행
================================================================================

  GitHub 서버에는 Linux cron 이 없고, 대신 Actions 의 schedule(cron)을 사용합니다.
  워크플로 파일: .github/workflows/daily-briefing.yml
  (UTC 00:00 = 한국 09:00, 한국은 일광절약시간 없음)

  [1] 저장소에 위 파일을 push 한 뒤

  [2] GitHub 웹 → 해당 저장소 → Settings → Secrets and variables → Actions
      → "New repository secret" 으로 아래 이름 그대로 등록 (값은 본인 config.py 와 동일):

        NAVER_CLIENT_ID
        NAVER_CLIENT_SECRET
        NEWSAPI_KEY
        OPENAI_API_KEY
        NOTION_TOKEN
        NOTION_DATABASE_ID

  [3] Actions 탭에서 워크플로가 활성화되어 있는지 확인
      (첫 push 후 수동 테스트: Actions → "Daily economic news briefing" → Run workflow)

  [4] GitHub Pages 로 브리핑 HTML 공개 (외부 사이트 iframe 등에 쓸 때)
      GitHub 웹 → 해당 저장소 → Settings → Pages
      → Build and deployment: Deploy from a branch
      → Branch: main, Folder: /docs  → Save

      설정 후 몇 분 뒤 아래 형태로 접속할 수 있습니다 (본인 계정·저장소 이름에 맞게):
        https://<GitHub사용자명>.github.io/<저장소명>/briefing.html

      briefing.html 은 매 실행마다 덮어쓰여 최신 브리핑이 됩니다.
      날짜별 파일은 news_YYYYMMDD.html 입니다.

  참고:
    - schedule 실행은 트래픽에 따라 몇 분 지연될 수 있습니다.
    - 비공개 저장소는 Actions 무료 분 제한이 있습니다. 공개 저장소는 정책이 다릅니다.
    - 장기간 저장소에 활동이 없으면 schedule 이 비활성화될 수 있으니, 가끔 push 하거나
      Actions 탭에서 다시 켜 주세요.


================================================================================
                        보안 주의사항
================================================================================

  ⚠ config.py에는 API 키가 들어가므로 반드시 로컬에만 보관하세요.
  ⚠ GitHub 등에 config.py를 업로드하지 마세요. (자동 비활성화될 수 있음)
  ⚠ 이 프로젝트는 .gitignore 에 config.py 가 포함되어 있습니다.


================================================================================
                        실행 요약 (한 번에 보기)
================================================================================

  1. python -m venv venv
  2. venv\Scripts\activate
  3. pip install -r requirements.txt
  4. copy .config.sample.py config.py
  5. config.py 열어서 API 키 입력 (apikey_how.md 참고)
  6. python main.py

  → Notion에서 오늘의 경제 뉴스 브리핑 페이지 확인, docs/ 에 HTML 생성
  → GitHub에 올린 뒤 Pages([4] 참고)를 켜 두면 briefing.html 을 웹·iframe에서 사용 가능


================================================================================
