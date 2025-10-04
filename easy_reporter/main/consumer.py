import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import websockets

LLM_WS_URL = "ws://llm-service:8001/ws"

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("✅ WebSocket connected (client ↔ Django)")

        # LLM 서버 연결 시도
        self.llm_ws = None
        try:
            self.llm_ws = await websockets.connect(LLM_WS_URL)
            print("🤖 Connected to LLM service")
            self.llm_available = True
        except Exception as e:
            print("⚠️ LLM 서버 연결 실패:", e)
            self.llm_available = False

    async def disconnect(self, close_code):
        print("❌ WebSocket disconnected (client ↔ Django)")
        if self.llm_ws and self.llm_ws.open:
            await self.llm_ws.close()
            print("🔌 LLM connection closed")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")

        # LLM 서버가 연결되어 있을 경우
        if self.llm_available and self.llm_ws:
            try:
                await self.llm_ws.send(json.dumps({"message": message}))
                llm_response = await self.llm_ws.recv()
                await self.send(json.dumps({"message": f"🤖 {llm_response}"}))
                return
            except Exception as e:
                print("⚠️ LLM 통신 오류:", e)
                self.llm_available = False  # 연결 끊김 표시

        # fallback: LLM 서버 없음 (mock 응답)
        await asyncio.sleep(0.2)
        await self.send(json.dumps({
            "message": f"LLM 서버 미연결 (Echo): {message}"
        }))
