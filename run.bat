@echo off
chcp 65001 > nul
echo [%date% %time%] 경제 뉴스 브리핑 시작...

REM ↓ 본인의 프로젝트 경로로 변경하세요
cd /d C:\projects\economic_news_bot

REM 파이썬 실행 (가상환경 사용 시 아래 주석 해제)
REM call venv\Scripts\activate.bat

python main.py

echo [%date% %time%] 완료.
