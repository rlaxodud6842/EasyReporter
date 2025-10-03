from django.http import JsonResponse

def chat_popup(request):
    return JsonResponse({"reply": "여기는 LLM 챗봇 팝업입니다."})
