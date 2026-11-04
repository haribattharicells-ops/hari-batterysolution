import telebot, openai, base64, os
from langdetect import detect

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")
CHANNEL_ID = -1004339378274

bot = telebot.TeleBot(BOT_TOKEN)
client = openai.OpenAI(api_key=OPENAI_KEY)

LANG_MAP = {"ta": "Tamil", "en": "English", "hi": "Hindi"}

def get_lang(text):
    try:
        lang = detect(text)
        if lang not in LANG_MAP: lang = "ta"
        return lang
    except: return "ta"

def ask_gpt(prompt, lang_code, image_b64=None):
    lang_name = LANG_MAP.get(lang_code, "Tamil")
    system = f"You are Hari Battery expert. Reply ONLY in {lang_name} language. User language is {lang_name}. If Tamil, use Thalaivare style. If Hindi/English, use respectful style."
    messages = [{"role": "system", "content": system}]
    if image_b64:
        messages.append({"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
        ]})
    else:
        messages.append({"role": "user", "content": prompt})
    res = client.chat.completions.create(model="gpt-4o", messages=messages)
    return res.choices[0].message.content

@bot.message_handler(content_types=['text'])
@bot.channel_post_handler(content_types=['text'])
def text_handler(message):
    text = message.text or message.channel_post.text if hasattr(message, 'channel_post') else message.text
    lang = get_lang(text)
    reply = ask_gpt(text, lang)
    bot.send_message(message.chat.id if hasattr(message, 'chat') else CHANNEL_ID, reply)

@bot.message_handler(content_types=['photo'])
@bot.channel_post_handler(content_types=['photo'])
def photo_handler(message):
    chat_id = message.chat.id
    file_id = message.photo[-1].file_id
    f = bot.get_file(file_id)
    img = bot.download_file(f.file_path)
    b64 = base64.b64encode(img).decode()
    caption = message.caption if hasattr(message, 'caption') and message.caption else "What is fault in this battery?"
    lang = get_lang(caption)
    prompt = f"Analyze this battery image fault. Question: {caption}"
    reply = ask_gpt(prompt, lang, b64)
    bot.send_message(chat_id, f"🔍 {reply}")

@bot.message_handler(content_types=['voice'])
def voice_handler(message):
    file_info = bot.get_file(message.voice.file_id)
    voice_file = bot.download_file(file_info.file_path)
    with open("voice.ogg", "wb") as f: f.write(voice_file)
    with open("voice.ogg", "rb") as f:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=f)
    text = transcript.text
    lang = get_lang(text)
    reply_text = ask_gpt(text, lang)
    tts = client.audio.speech.create(model="tts-1", voice="alloy", input=reply_text)
    tts.stream_to_file("reply.mp3")
    bot.send_message(message.chat.id, f"🗣️ Heard ({LANG_MAP[lang]}): {text}\n\n💬 Reply: {reply_text}")
    with open("reply.mp3", "rb") as v:
        bot.send_voice(message.chat.id, v)

print("VIP 3 Language Bot READY! Tamil, English, Hindi!")
bot.infinity_polling()
