# Python 환경 기반
FROM python:3.11-slim

# Python이 pyc 파일 생성 안 하게 + 로그 버퍼링 끄기
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 컨테이너 내부 작업 폴더
WORKDIR /app

# 호스트의 requirements.txt 복사 후 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 전체 코드 복사
COPY . .

# 컨테이너 내부 포트 지정 (정보용)
EXPOSE 8000

# Django 실행 명령
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
