from fastapi import FastAPI, Request, HTTPException
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = FastAPI()

# ใช้ ENV จาก Vercel
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.get("/")
async def root():
    return {"status": "ok", "message": "LINE Bot is running!"}

@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("x-line-signature")
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # ตอบกลับข้อความเดิม
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"คุณพิมพ์ว่า: {event.message.text}")
    )
