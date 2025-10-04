# Python 환경 기반
FROM python:3.11-slim

# Python이 pyc 파일 생성 안 하게 + 로그 버퍼링 끄기
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 컨테이너 내부 작업 폴더
WORKDIR /app

# requirements.txt 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Channels + Uvicorn (없다면 설치)
RUN pip install uvicorn[standard] channels

# 코드 복사
COPY . .

# 포트 정보
EXPOSE 8000

# ASGI 실행 (Django Channels)
CMD ["uvicorn", "easy_reporter.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
