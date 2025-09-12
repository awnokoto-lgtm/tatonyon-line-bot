# main.py — Trip Planner + Quick Reply
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, Response
from linebot import LineBotApi, WebhookParser
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReply, QuickReplyButton, MessageAction,
    FlexSendMessage
)

# ====== ENV ======
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_TOKEN  = os.getenv("LINE_CHANNEL_TOKEN")
if not CHANNEL_SECRET or not CHANNEL_TOKEN:
    raise RuntimeError("Missing LINE_CHANNEL_SECRET or LINE_CHANNEL_TOKEN")

line_bot_api = LineBotApi(CHANNEL_TOKEN)
parser       = WebhookParser(CHANNEL_SECRET)

app = FastAPI(title="Tatonyon Trip Bot")

# ====== UTIL ======
def norm(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "")

# ====== QUICK REPLY ======
def qr_buttons():
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="เมนู", text="เมนู")),
        QuickReplyButton(action=MessageAction(label="โตเกียว5วัน", text="โตเกียว5วัน")),
        QuickReplyButton(action=MessageAction(label="คันไซ", text="โอซาก้า–เกียวโต")),
        QuickReplyButton(action=MessageAction(label="ซากุระ", text="ซากุระ")),
    ])

# ====== REPLIES ======
def reply_menu() -> str:
    return (
        "📌 เมนูแผนเที่ยวญี่ปุ่น (พิมพ์คีย์เวิร์ดเพื่อดูรายละเอียด)\n"
        "• โตเกียว5วัน  – แพลนเที่ยวเมือง + Day trip\n"
        "• โอซาก้า–เกียวโต – เส้นทางคันไซฮิต 4–5 วัน\n"
        "• ฮอกไกโด – ซัปโปโร/โอตารุ/บิเอะ\n"
        "• คิวชู – ฟุกุโอกะ/นางาซากิ/เบปปุ\n"
        "• ซากุระ – ช่วงแนะนำชมซากุระ\n"
        "• ใบไม้เปลี่ยนสี – จุดไฮไลต์\n"
        "• JR PASS – การเลือกตั๋วรถไฟ\n"
        "• SUICA – การ์ดจ่ายค่าเดินทาง\n"
        "• WIFI – ซิม/ไวไฟพกพา\n\n"
        "ลองพิมพ์: โตเกียว5วัน, โอซาก้า–เกียวโต, ฮอกไกโด, คิวชู, ซากุระ, ใบไม้เปลี่ยนสี, jrpass, suica, wifi"
    )

def plan_tokyo_5d() -> str:
    return (
        "🗼 โตเกียว 5 วัน (ตัวอย่างแผนคร่าวๆ)\n"
        "Day 1: สนามบิน→ที่พัก, ชินจูกุ/ชิบุยะ\n"
        "Day 2: อาซากุสะ–สกายทรี–อุเอโนะ/อากิฮาบาระ\n"
        "Day 3: Day Trip → ฟูจิ/คาวากุจิโกะ หรือ Nikko/Kamakura\n"
        "Day 4: โอไดบะ/TeamLab–Ginza–Tokyo Station\n"
        "Day 5: ซื้อของฝาก–สนามบิน\n\n"
        "💡 เดินทาง: ใช้ Suica/Pasmo สะดวกสุดในโตเกียว\n"
        "📎 เพิ่มเติม: https://www.gotokyo.org/en/"
    )

def plan_kansai() -> str:
    return (
        "⛩️ โอซาก้า–เกียวโต (4–5 วัน)\n"
        "Day 1: Osaka (Dotonbori–Shinsaibashi–Umeda)\n"
        "Day 2: Kyoto (Fushimi Inari–Kiyomizu–Gion)\n"
        "Day 3: Nara (Todaiji–สวนกวาง) + กลับโอซาก้า\n"
        "Day 4: Universal/Osaka Castle หรือ Kobe\n"
        "Day 5: ช้อปของฝาก–สนามบิน\n\n"
        "💡 บัตร: Kansai Thru Pass/ICOCA ขึ้นกับแผน\n"
        "📎 เพิ่มเติม: https://www.japan-guide.com/e/e2157.html"
    )

def plan_hokkaido() -> str:
    return (
        "❄️ ฮอกไกโด (6–7 วัน แบบย่อ)\n"
        "ซัปโปโร–โอตารุ–ฟุราโนะ/บิเอะ–โทยะ\n"
        "💡 หน้าหนาวมีเทศกาลหิมะ/ลานสกี\n"
        "📎 เพิ่มเติม: https://www.visit-hokkaido.jp/en/"
    )

def plan_kyushu() -> str:
    return (
        "🌋 คิวชู (ฟุกุโอกะ–นางาซากิ–คุมาโมโตะ–เบปปุ)\n"
        "แนะนำ 5–7 วัน: ฟุกุโอกะ→นางาซากิ→คุมาโมโตะ→ยูฟุอิน/เบปปุ\n"
        "📎 เพิ่มเติม: https://www.japan-guide.com/list/e1108.html"
    )

def info_sakura() -> str:
    return (
        "🌸 ซากุระโดยทั่วไป: ปลายมี.ค.–ต้นเม.ย. (โตเกียว/คันโต)\n"
        "คันไซใกล้เคียง / ฮอกไกโดช้ากว่า (ปลายเม.ย.–พ.ค.)\n"
        "📎 พยากรณ์: https://www.japan-guide.com/sakura/"
    )

def info_momiji() -> str:
    return (
        "🍁 ใบไม้เปลี่ยนสี: ปลายต.ค.–ปลายพ.ย. (คันโต/คันไซ)\n"
        "ฮอกไกโดเร็วกว่า (ปลายก.ย.–ต.ค.)\n"
        "📎 อัปเดต: https://www.japan-guide.com/fallcolor/"
    )

def info_jrpass() -> str:
    return (
        "🚄 JR PASS: เลือกตามเส้นทางจริง\n"
        "• เที่ยวเมืองเดียว → ไม่คุ้ม JR Pass\n"
        "• ข้ามภูมิภาคบ่อย ๆ → พิจารณา JR/Regional Pass\n"
        "📎 เปรียบเทียบ: https://www.japan-guide.com/e/e2357.html"
    )

def info_suica() -> str:
    return (
        "💳 SUICA/PASMO/ICOCA = บัตรแตะจ่ายรถไฟ/บัส/ร้านสะดวกซื้อ\n"
        "ซื้อ/เติมได้ที่สถานีใหญ่ เครื่องอัตโนมัติใช้งานง่าย\n"
        "📎 วิธีใช้: https://www.japan-guide.com/e/e2359_003.html"
    )

def info_wifi() -> str:
    return (
        "📶 อินเทอร์เน็ตญี่ปุ่น: ซิม/ไวไฟพกพา\n"
        "• ซิมเหมาะไปเดี่ยว/คู่\n"
        "• WiFi Pocket เหมาะไปหลายคน แชร์สะดวก"
    )

def unknown_help() -> str:
    return (
        "พิมพ์ 'เมนู' เพื่อดูตัวเลือกทั้งหมด\n"
        "เช่น: โตเกียว5วัน, โอซาก้า–เกียวโต, ฮอกไกโด, คิวชู, ซากุระ, ใบไม้เปลี่ยนสี, jrpass, suica, wifi"
    )

# ====== ROUTES ======
@app.get("/")
async def root():
    return {"message": "Japan Trip Bot is running!"}

@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)

# ====== WEBHOOK ======
@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("x-line-signature")
    body = await request.body()

    try:
        events = parser.parse(body.decode("utf-8"), signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            user_text_raw = event.message.text or ""
            key = norm(user_text_raw)

            if key in ["เมนู", "menu"]:
                reply = reply_menu()
            elif "โตเกียว5วัน" in key or "tokyo5" in key:
                reply = plan_tokyo_5d()
            elif ("โอซาก้า–เกียวโต" in user_text_raw) or ("โอซาก้า-เกียวโต" in user_text_raw) or ("คันไซ" in user_text_raw) or ("kansai" in key):
                reply = plan_kansai()
            elif ("ฮอกไกโด" in key) or ("hokkaido" in key) or ("ซัปโปโร" in key):
                reply = plan_hokkaido()
            elif ("คิวชู" in key) or ("kyushu" in key) or ("ฟุกุโอกะ" in key):
                reply = plan_kyushu()
            elif ("ซากุระ" in key) or ("sakura" in key):
                reply = info_sakura()
            elif ("ใบไม้เปลี่ยนสี" in key) or ("momiji" in key) or ("autumn" in key):
                reply = info_momiji()
            elif ("jrpass" in key) or ("jr pass" in user_text_raw.lower()):
                reply = info_jrpass()
            elif ("suica" in key) or ("pasmo" in key) or ("icoca" in key):
                reply = info_suica()
            elif ("wifi" in key) or ("ซิม" in user_text_raw):
                reply = info_wifi()
            else:
                reply = f"บอทตอบ: {user_text_raw}\n\n{unknown_help()}"

            # ✅ ใส่ Quick Reply ทุกครั้งที่ตอบ
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply, quick_reply=qr_buttons())
            )

    return JSONResponse({"status": "ok"})
