from django.http import JsonResponse

def test_ai(request):
    return JsonResponse({"message": "AI 모듈 연결 테스트"})
