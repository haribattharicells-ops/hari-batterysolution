from flask import Flask
import threading
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Live!"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()
import telebot
import requests
import os
from gtts import gTTS
from openai import OpenAI
from datetime import datetime

# --- CONFIG ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
PRIVATE_CHANNEL_ID = -1004339378274
PAYMENT_LINK = "https://chanpay.in/haribattery"
COURSE_PRICE = "Rs.99 Only"

bot = telebot.TeleBot(BOT_TOKEN)
openai_client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

def send_to_private(user, q, ans, ai_name):
    try:
        log = f"LOG [{ai_name}]\nUser: {user}\nQ: {q}\nA: {ans[:500]}...\nTime: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
        bot.send_message(PRIVATE_CHANNEL_ID, log)
    except:
        pass

@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message, "Vanakkam Thalaivare! 🔋\n\nHari Battery Solutions VIP Course - Rs.99 Only!\n\nPayment Link: " + PAYMENT_LINK + "\n\nPayment pannitu Screenshot anupunga!\n\nEnna venum? Battery pathi ethu venalum kelunga!")

@bot.message_handler(commands=['pay', 'course', 'price'])
def pay(message):
    bot.reply_to(message, "📚 Hari Battery VIP Course\n\nPrice: " + COURSE_PRICE + "\n\nPayment Link: " + PAYMENT_LINK + "\n\nPayment pannitu Screenshot anupunga, VIP Channel link tharom!")

@bot.message_handler(commands=['call'])
def call(message):
    bot.reply_to(message, "📞 Hari Anna: 98410 12345\n\nAana enkitteye kelunga Thalaivare, naane pathil solliduren!")

def ask_gemini(question):
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY
        data = {"contents": [{"parts": [{"text": "You are Hari Battery Solutions expert. Answer in Tamil, simple Tanglish, friendly like Thalaivare style. Question: " + question}]}]}
        res = requests.post(url, json=data, timeout=20)
        return res.json()["candidates"][0]["content"]["parts"][0]["text"], "Gemini"
    except:
        try:
            r = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You are Hari Battery Solutions expert. Answer in Tamil Tanglish, friendly Thalaivare style."}, {"role": "user", "content": question}]
            )
            return r.choices[0].message.content, "ChatGPT-Backup"
        except:
            return "Sorry Thalaivare, konjam network problem. Thirumba kelunga!", "Error"

def send_voice(chat_id, text):
    try:
        tts = gTTS(text=text, lang='ta', slow=False)
        tts.save("reply.mp3")
        with open("reply.mp3", "rb") as audio:
            bot.send_voice(chat_id, audio)
    except:
        bot.send_message(chat_id, text)

@bot.message_handler(content_types=['voice'])
def voice_handler(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded = bot.download_file(file_info.file_path)
        with open("voice.ogg", "wb") as f:
            f.write(downloaded)
        bot.reply_to(message, "Kural ketuchu Thalaivare! Konjam wait pannunga...")
        answer, ai_name = ask_gemini("User sent a voice message in Tamil about battery. Reply in Tamil, simple.")
        send_voice(message.chat.id, answer)
        send_to_private(message.from_user.first_name, "Voice Message", answer, ai_name)
    except:
        bot.reply_to(message, "Voice-la problem Thalaivare, text-la kelunga!")

@bot.message_handler(func=lambda m: True)
def all_msg(message):
    text = message.text.lower() if message.text else ""
    if "vanakkam" in text or "hi" in text or "hello" in text:
        bot.reply_to(message, "Vanakkam Thalaivare! 🙏 Enna venum? Course venuma? /pay -nu type pannunga!")
        return
    if "course" in text or "price" in text or "vilai" in text or "99" in text:
        bot.reply_to(message, "📚 VIP Course - Rs.99 Only!\n\nPayment Link: " + PAYMENT_LINK)
        return
    ans, ai_name = ask_gemini(message.text)
    bot.reply_to(message, ans)
    if len(ans) > 100:
        send_voice(message.chat.id, ans[:300])
    send_to_private(f"{message.from_user.first_name} (@{message.from_user.username})", message.text, ans, ai_name)

import threading

def run_bot():
    print("Hari Battery Solutions Bot Started...")
    bot.infinity_polling()

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
