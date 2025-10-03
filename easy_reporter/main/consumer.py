import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import websockets  # LLM 도커와 웹소켓 통신용

LLM_WS_URL = "ws://llm-service:8001/ws"  # LLM 도커 웹소켓 주소

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.llm_ws = await websockets.connect(LLM_WS_URL)

    async def disconnect(self, close_code):
        await self.llm_ws.close()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")
        try:
            await self.llm_ws.send(json.dumps({"message": message}))
            llm_response = await self.llm_ws.recv()
            await self.send(text_data=json.dumps({"message": llm_response}))
        except Exception as e:
            await self.send(text_data=json.dumps({"message": "LLM 연결 오류"}))
