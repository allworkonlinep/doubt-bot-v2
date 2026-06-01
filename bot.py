import os,logging,base64,threading
from http.server import HTTPServer,BaseHTTPRequestHandler
import requests as req
from telegram import Update
from telegram.ext import ApplicationBuilder,CommandHandler,MessageHandler,filters,ContextTypes

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s",level=logging.INFO)
logger=logging.getLogger(__name__)

TELEGRAM_TOKEN=os.environ["TELEGRAM_TOKEN"]
GROQ_API_KEY=os.environ["GROQ_API_KEY"]
URL="https://api.groq.com/openai/v1/chat/completions"
HDR={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"}
SYS="""Tu ek expert teacher hai jo students ki problems solve karta hai.

LANGUAGE RULE: Student jis language mein sawaal kare, USI language mein jawab do.
- Hindi mein pucha to Hindi mein jawab do
- English mein pucha to English mein jawab do
- Hinglish mein pucha to Hinglish mein jawab do

LENGTH RULE: Sawaal jitna chota, jawab utna chota. Sawaal jitna bada, jawab utna detail mein.
- Simple sawaal jaise 2+2 = sirf answer do, zyada explanation mat do
- Complex sawaal = step-by-step detail mein batao

IMPORTANT RULES:
1. Koi LaTeX mat use karo - frac, sqrt, sin jaise symbols bilkul nahi
2. Math plain text mein likho: 2/3 likho, sqrt(x) likho
3. Subject identify karo
4. End mein ek short tip do

Format:
Subject: [name]
Solution: [answer]
Tip: [tip]"""

def ask(msgs):
    r=req.post(URL,headers=HDR,json={"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":msgs,"max_tokens":1500},timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def log_message(self,*a):pass

def run_server():
    port=int(os.environ.get("PORT",8080))
    HTTPServer(("0.0.0.0",port),H).serve_forever()

async def start(u,c):
    await u.message.reply_text(
"🌟━━━━━━━━━━━━━━━━━━━━🌟\n"
"   🎓 *D O U B T  S O L V E R*\n"
"🌟━━━━━━━━━━━━━━━━━━━━🌟\n\n"
"⚡ *Powered by Artificial Intelligence*\n"
"🔥 Created by *S H I V A M  G U P T A*\n\n"
"╔══════════════════════╗\n"
"║  📸 Photo → Instant Solution  ║\n"
"║  ✍️ Text  → Step-by-Step      ║\n"
"║  🧠 AI    → Smart Explain     ║\n"
"╚══════════════════════╝\n\n"
"📚 *Math • Science • Hindi • English*\n"
"💯 Bilkul FREE • Har Sawaal Ka Jawab\n\n"
"🚀 *Apna pehla sawaal bhejo!*",
parse_mode="Markdown")

async def text(u,c):
    await u.message.reply_text("🤔 Solve kar raha hoon...")
    try:
        ans=ask([{"role":"system","content":SYS},{"role":"user","content":u.message.text}])
        await u.message.reply_text(ans)
    except Exception as e:
        await u.message.reply_text(f"❌ Error: {str(e)[:200]}")

async def photo(u,c):
    await u.message.reply_text("📸 Dekh raha hoon...")
    try:
        f=await c.bot.get_file(u.message.photo[-1].file_id)
        b=await f.download_as_bytearray()
        img=base64.standard_b64encode(b).decode()
        cap=u.message.caption or "Is image ka question solve karo"
        ans=ask([{"role":"system","content":SYS},{"role":"user","content":[{"type":"text","text":cap},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img}"}}]}])
        await u.message.reply_text(ans)
    except Exception as e:
        await u.message.reply_text(f"❌ Error: {str(e)[:200]}")

threading.Thread(target=run_server,daemon=True).start()
app=ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(MessageHandler(filters.PHOTO,photo))
app.add_handler(MessageHandler(filters.TEXT&~filters.COMMAND,text))
logger.info("✅ Bot chal raha hai...")
app.run_polling(stop_signals=None)
