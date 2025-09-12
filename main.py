# main.py
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, Response
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage

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
        "Day 1: สนามบิน→ที่พัก, ชินจูกุ/ชิบุยะ, จุดชมวิวโตเกียว\n"
        "Day 2: วัดอาซากุสะ–โตเกียวสกายทรี–อุเอโนะ/อากิฮาบาระ\n"
        "Day 3: Day Trip → ฟูจิ/คาวากุจิโกะ หรือ Nikko/Kamakura\n"
        "Day 4: โอไดบะ/TeamLab–กินเที่ยวย่าน Ginza–Tokyo Station\n"
        "Day 5: ซื้อของฝาก–สนามบิน\n\n"
        "💡 การเดินทาง: IC Card (Suica/Pasmo) สะดวกสุดในโตเกียว\n"
        "📎 เพิ่มเติม: https://www.gotokyo.org/en/  (ข้อมูลทางการ)"
    )

def plan_kansai() -> str:
    return (
        "⛩️ โอซาก้า–เกียวโต (4–5 วัน)\n"
        "Day 1: โอซาก้า (Dotonbori–Shinsaibashi–Umeda Sky)\n"
        "Day 2: เกียวโต (Fushimi Inari–Kiyomizu–Gion)\n"
        "Day 3: นารา (Todaiji–สวนกวาง) + กลับโอซาก้า\n"
        "Day 4: Universal/Osaka Castle หรือ Kobe\n"
        "Day 5: ช้อปของฝาก–สนามบิน\n\n"
        "💡 บัตรแนะนำ: Kansai Thru Pass/ICOCA ขึ้นกับแผน\n"
        "📎 เพิ่มเติม: https://www.japan-guide.com/e/e2157.html"
    )

def plan_hokkaido() -> str:
    return (
        "❄️ ฮอกไกโด (6–7 วัน แบบย่อ)\n"
        "ซัปโปโร–โอตารุ–นิงเกิ้ลเทอเรส/ฟุราโนะ–บิเอะ–ทะเลสาบโทยะ\n"
        "ถ้าหน้าหนาว: เทศกาลหิมะซัปโปโร, ลานสกี\n"
        "💡 รถเช่า/บัส/รถไฟ ขึ้นกับเส้นทางและฤดูกาล\n"
        "📎 เพิ่มเติม: https://www.visit-hokkaido.jp/en/"
    )

def plan_kyushu() -> str:
    return (
        "🌋 คิวชู (ฟุกุโอกะ–นางาซากิ–คุมาโมโตะ–เบปปุ)\n"
        "แนะนำ 5–7 วัน: ฟุกุโอกะ(กิน–ช้อป)→นางาซากิ(Glovers/Dejima)\n"
        "→คุมาโมโตะ(ปราสาท)→ยูฟุอิน/เบปปุ(ออนเซ็น)\n"
        "📎 เพิ่มเติม: https://www.japan-guide.com/list/e1108.html"
    )

def info_sakura() -> str:
    return (
        "🌸 ซากุระญี่ปุ่นโดยทั่วไป: ปลายมี.ค.–ต้นเม.ย. (โตเกียว/คันโต)\n"
        "คันไซ: ช่วงเวลาใกล้เคียงกัน / ฮอกไกโดช้ากว่า (ปลายเม.ย.–พ.ค.)\n"
        "📎 ดูพยากรณ์อัปเดต: https://www.japan-guide.com/sakura/\n"
        "💡 ทริค: เช็กพยากรณ์ใกล้วันเดินทางอีกครั้ง"
    )

def info_momiji() -> str:
    return (
        "🍁 ใบไม้เปลี่ยนสี (โมมิจิ) ช่วงทั่วไป: ปลายต.ค.–ปลายพ.ย.\n"
        "คันไซ/คันโต: พีคประมาณพ.ย. / ฮอกไกโดเร็วกว่า (ปลายก.ย.–ต.ค.)\n"
        "📎 ติดตามอัปเดต: https://www.japan-guide.com/fallcolor/\n"
        "💡 จุดฮิต: Arashiyama, Kiyomizu, Meiji Jingu Gaien, Nikko"
    )

def info_jrpass() -> str:
    return (
        "🚄 JR PASS/ตั๋วรถไฟ: เลือกตามเส้นทางจริง\n"
        "• Tokyo only → ไม่คุ้ม JR Pass, ใช้ IC Card/ตั๋วรายวัน\n"
        "• วิ่งข้ามภูมิภาคบ่อย ๆ → ค่อยพิจารณา JR Pass/Regional Pass\n"
        "📎 เปรียบเทียบแพ็กเกจ: https://japanrailpass.net/  และ https://www.japan-guide.com/e/e2357.html"
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
        "• ซิม Data 7–15GB เหมาะไปเดี่ยว/คู่\n"
        "• WiFi Pocket เหมาะไปกันหลายคน แชร์สะดวก\n"
        "📎 เปรียบเทียบแพ็กเกจ: ลองเช็คผู้ให้บริการในไทย + รีวิวล่าสุด"
    )

def unknown_help() -> str:
    return (
        "พิมพ์ 'เมนู' เพื่อดูตัวเลือกทั้งหมด\n"
        "ตัวอย่าง: โตเกียว5วัน, โอซาก้า–เกียวโต, ฮอกไกโด, คิวชู, ซากุระ, ใบไม้เปลี่ยนสี, jrpass, suica, wifi"
    )

# ====== ROUTES (health) ======
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
            elif "โอซาก้า–เกียวโต" in user_text_raw or "โอซาก้า-เกียวโต" in user_text_raw or "คันไซ" in user_text_raw or "kansai" in key:
                reply = plan_kansai()
            elif "ฮอกไกโด" in key or "hokkaido" in key or "ซัปโปโร" in key:
                reply = plan_hokkaido()
            elif "คิวชู" in key or "kyushu" in key or "ฟุกุโอกะ" in key:
                reply = plan_kyushu()
            elif "ซากุระ" in key or "sakura" in key:
                reply = info_sakura()
            elif "ใบไม้เปลี่ยนสี" in key or "momiji" in key or "autumn" in key:
                reply = info_momiji()
            elif "jrpass" in key or "jr pass" in user_text_raw.lower():
                reply = info_jrpass()
            elif "suica" in key or "pasmo" in key or "icoca" in key:
                reply = info_suica()
            elif "wifi" in key or "ซิม" in user_text_raw:
                reply = info_wifi()
            elif "ช่วย" in user_text_raw or "help" in key:
                reply = unknown_help()
            else:
                reply = f"บอทตอบ: {user_text_raw}\n\n{unknown_help()}"

            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

    return JSONResponse({"status": "ok"})
