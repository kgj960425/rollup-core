# vercelExample


# 가상 환경 생성
python -m venv venv

# requirements.txt 설치 명령어
pip install -r requirements.txt

# venv 환경 실행 명령어
.\venv\Scripts\activate;

# 서버 실행 명령어 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info