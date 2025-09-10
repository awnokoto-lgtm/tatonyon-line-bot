# main.py
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, Response
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = FastAPI()

CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_TOKEN  = os.getenv("LINE_CHANNEL_TOKEN")

if not CHANNEL_SECRET or not CHANNEL_TOKEN:
    raise RuntimeError("Missing LINE_CHANNEL_SECRET or LINE_CHANNEL_TOKEN")

line_bot_api = LineBotApi(CHANNEL_TOKEN)
parser = WebhookParser(CHANNEL_SECRET)

@app.get("/")
def root():
    return {"message": "LINE Bot is running!"}

@app.get("/favicon.ico")
def fav():
    return Response(status_code=204)

@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("X-Line-Signature")
    body = (await request.body()).decode("utf-8")

    try:
        events = parser.parse(body, signature)
    except Exception as e:
        # ลง Log ง่าย ๆ
        raise HTTPException(status_code=400, detail=f"Bad signature or parse error: {e}")

    for ev in events:
        if isinstance(ev, MessageEvent) and isinstance(ev.message, TextMessage):
            # ตอบกลับข้อความที่ผู้ใช้ส่งมา
            line_bot_api.reply_message(
                ev.reply_token,
                TextSendMessage(text=f"บอทตอบ: {ev.message.text}")
            )
    return JSONResponse({"status": "ok"})
