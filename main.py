# main.py
import os
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage

CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_TOKEN  = os.getenv("LINE_CHANNEL_TOKEN")

if not CHANNEL_SECRET or not CHANNEL_TOKEN:
    raise RuntimeError("Missing LINE_CHANNEL_SECRET or LINE_CHANNEL_TOKEN")

line_bot_api = LineBotApi(CHANNEL_TOKEN)
parser = WebhookParser(CHANNEL_SECRET)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "LINE Bot is running!"}

@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)

@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("X-Line-Signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing X-Line-Signature")

    body = await request.body()
    body = body.decode("utf-8")

    try:
        events = parser.parse(body, signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid signature: {e}")

    for event in events:
        # รับเฉพาะข้อความ
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            user_text = (event.message.text or "").strip()
            norm = user_text.lower()

            # ---- กติกาตอบกลับ ----
            # 1) เมนู
            if user_text in ["เมนู", "MENU", "Menu", "/menu"]:
                reply_text = (
                    "🍽️ เมนูวันนี้\n"
                    "• ข้าวหน้าไก่\n"
                    "• ข้าวแกงกะหรี่\n"
                    "• ราเมงชาชู\n"
                    "สั่งเมนูพิมพ์: สั่ง + ชื่อเมนู เช่น `สั่ง ราเมงชาชู`"
                )

            # 2) เที่ยวญี่ปุ่น
            elif "เที่ยวญี่ปุ่น" in user_text or "japan travel" in norm:
                reply_text = (
                    "✈️ รวมทริปเที่ยวญี่ปุ่นที่แอ๋วแนะนำ\n"
                    "👉 https://tatonyon-guidejp.example/ (ปรับเป็นลิงก์จริงของแอ๋วได้เลย)\n"
                    "มีคำถามบอกแอ๋วได้เลยน้า"
                )

            # 3) สวัสดี / hello / hi
            elif user_text in ["สวัสดี", "สวัสดีค่ะ", "สวัสดีครับ"] or norm in ["hello", "hi", "hey"]:
                reply_text = "สวัสดีค่า 😊 ต้องการดูเมนูพิมพ์ `เมนู` หรือถาม `เที่ยวญี่ปุ่น` ได้เลย"

            # 4) คำอื่น ๆ → echo
            else:
                reply_text = f"บอทตอบ: {user_text}"

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )

    return JSONResponse({"status": "ok"})
