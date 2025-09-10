from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = FastAPI()

# ดึงค่าจาก Environment Variables (ตั้งไว้ใน Vercel)
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_TOKEN = os.getenv("LINE_CHANNEL_TOKEN")

if LINE_CHANNEL_SECRET is None or LINE_CHANNEL_TOKEN is None:
    raise Exception("LINE_CHANNEL_SECRET or LINE_CHANNEL_TOKEN is not set. Check Vercel Environment Variables.")

line_bot_api = LineBotApi(LINE_CHANNEL_TOKEN)
parser = WebhookParser(LINE_CHANNEL_SECRET)


# ✅ Route หลัก ใช้เช็กว่าเซิร์ฟเวอร์รันอยู่
@app.get("/")
async def root():
    return {"message": "LINE Bot is running!"}


# ✅ กัน error เวลา Vercel เรียก favicon.ico
@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(content={"status": "no favicon"})


# ✅ Webhook ที่ LINE จะยิงมา
@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    body_text = body.decode("utf-8")

    try:
        events = parser.parse(body_text, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature. Check LINE_CHANNEL_SECRET.")

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            # ส่งข้อความตอบกลับ
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"คุณพิมพ์ว่า: {event.message.text}")
            )

    return {"status": "ok"}
