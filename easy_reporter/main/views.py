import requests
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.http import JsonResponse
from .models import ViolationReport
import json


def home(request):
    return render(request, 'main/index.html')


@csrf_exempt
def upload_image(request):
    if request.method == "POST" and request.FILES.get('image'):
        image_file = request.FILES['image']
        
        # FastAPI 테스트용 호출
        res = requests.post('http://altclip-api:8000/ocr',files={'file':(image_file.name,image_file.read(),image_file.content_type)})
        
        result_value = res.json().get('results', [])
        if result_value:
            text_value = result_value[0].get('text')  # 리스트의 첫 번째 요소의 text만 추출
            print("OCR 텍스트 결과:", text_value)
            return JsonResponse({'plate': text_value})
        else:
            return JsonResponse({'text': ''})  # 결과가 비어있을 때 안전하게 처리
    return JsonResponse({'error': 'No file uploaded'}, status=400)
# 내부 Docker 네트워크 기준 URL
LLM_API_URL = "http://llm-service:8001/ask"

@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message", "")
            if not message:
                return JsonResponse({"message": "메시지를 입력해주세요."}, status=400)

            res = requests.post(LLM_API_URL, json={"question": message})
            llm_data = res.json()
            return JsonResponse({"message": llm_data.get("answer", "응답이 없습니다.")})

        except Exception as e:
            print("❌ LLM API 호출 오류:", e)
            return JsonResponse({"message": "LLM 서버에 연결할 수 없습니다."}, status=500)
    return JsonResponse({"message": "잘못된 요청입니다."}, status=405)


@csrf_exempt
def submit_report(request):
    if request.method == "POST":
        # JSON + 파일 데이터 처리
        violation_type = request.POST.get("violation_type")
        location = request.POST.get("location")
        plate_number = request.POST.get("plate_number")
        image_file = request.FILES.get("image")

        if not all([violation_type, location, plate_number, image_file]):
            return JsonResponse({
                "status": "error",
                "message": "모든 데이터를 입력하세요."
            }, status=400)

        report = ViolationReport.objects.create(
            violation_type=violation_type,
            location=location,
            plate_number=plate_number,
            image=image_file
        )

        return JsonResponse({
            "status": "success",
            "report_id": report.id,
            "date": report.date.strftime("%Y-%m-%d %H:%M:%S"),
            "image_url": report.image.url
        })

    return JsonResponse({
        "status": "error",
        "message": "Invalid request"
    }, status=400)