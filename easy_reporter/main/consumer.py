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
        """
        브라우저에서 메시지를 받으면 LLM 서버로 전달하고,
        LLM 서버로부터 chunk 단위로 받은 데이터를 다시 브라우저로 전송.
        """
        data = json.loads(text_data)
        message = data.get("message", "")

        # LLM 서버가 연결되어 있다면
        if self.llm_available and self.llm_ws:
            try:
                # 1) 스트리밍 시작 알림
                await self.send(json.dumps({"type": "stream_start"}))

                # 2) LLM 서버로 질문 전송
                await self.llm_ws.send(json.dumps({"question": message}))

                # 3) LLM으로부터 chunk 수신
                while True:
                    chunk_raw = await self.llm_ws.recv()
                    chunk = json.loads(chunk_raw)

                    # 종료 신호
                    if chunk["type"] == "end":
                        await self.send(json.dumps({"type": "stream_end"}))
                        break

                    # chunk 데이터일 경우 클라이언트로 중계
                    if chunk["type"] == "chunk":
                        await self.send(json.dumps({
                            "type": "chunk",
                            "message": chunk["data"]
                        }))

            except Exception as e:
                print("⚠️ LLM 통신 오류:", e)
                self.llm_available = False
                await self.send(json.dumps({
                    "type": "error",
                    "message": f"LLM 서버와의 통신 오류: {e}"
                }))
            return

        # LLM 서버 연결이 안 되어 있는 경우 fallback
        await asyncio.sleep(0.2)
        await self.send(json.dumps({
            "type": "chunk",
            "message": f"(mock) {message}"
        }))
        await self.send(json.dumps({"type": "stream_end"}))
