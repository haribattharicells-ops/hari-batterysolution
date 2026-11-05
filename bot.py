
import telebot
import requests
import os
from gtts import gTTS
from openai import OpenAI
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
PRIVATE_CHANNEL_ID = -1004339378274
PAYMENT_LINK = "https://chanpay.in/haribattery"

bot = telebot.TeleBot(BOT_TOKEN)
openai_client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

def send_to_private(user, q, ans, ai_name):
    try:
        log = f"🔒 HARI BATTERY LOG [{ai_name}]\n👤 {user}\n💬 Q: {q}\n🤖 A: {ans[:500]}...\n⏰ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
        bot.send_message(PRIVATE_CHANNEL_ID, log)
    except:
        pass

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Vanakkam Thalaivare! 🔋\n\nHari Battery Solutions VIP Course - Rs.99 Only!\n\nPayment pannunga, VIP Channel-la sernthudalam!\n\nPayment Link: " + PAYMENT_LINK + "\n\nPayment pannitu Screenshot anupunga!")

@bot.message_handler(commands=['pay'])
def pay(message):
    bot.reply_to(message, "Payment Link: " + PAYMENT_LINK + "\n\nRs.99 - VIP Course")

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
        except Exception as e:
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
    except Exception as e:
        bot.reply_to(message, "Voice-la problem Thalaivare, text-la kelunga!")

@bot.message_handler(func=lambda m: True)
def all_msg(message):
    ans, ai_name = ask_gemini(message.text)
    bot.reply_to(message, ans)
    send_to_private(f"{message.from_user.first_name} (@{message.from_user.username})", message.text, ans, ai_name)

print("Hari Battery Solutions Bot Started...")
bot.infinity_polling()
