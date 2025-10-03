# main/models.py
from django.db import models

class ViolationReport(models.Model):
    date = models.DateTimeField(auto_now_add=True)  # 신고 생성 시 자동 기록
    violation_type = models.CharField(max_length=100)  # 예: "신호위반", "주차위반"
    location = models.CharField(max_length=255)       # 위치 (주소 문자열)
    plate_number = models.CharField(max_length=20)    # 차량 번호
    image = models.ImageField(upload_to='reports/%Y/%m/%d/')  # 업로드된 이미지 저장 경로

    def __str__(self):
        return f"{self.plate_number} - {self.violation_type} ({self.date:%Y-%m-%d %H:%M})"