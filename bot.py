import logging, requests, random
from gtts import gTTS
from textblob import TextBlob
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CallbackQueryHandler
from telegram.ext import RegexHandler, Filters, CommandHandler, MessageHandler, ConversationHandler


gen_key, weather_key, tts_key, phr_key, calc_key = range(5)


def create_log():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)


def set_updaters(dispatcher):
    # Старт
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.regex("Назад в меню"), start))
    dispatcher.add_handler(MessageHandler(Filters.regex("О создателях"), about))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('Генератор паролей'), gen1),
            MessageHandler(Filters.regex('Погода'), weather1),
            MessageHandler(Filters.regex('Озвучка голосом'), tts1),
            MessageHandler(Filters.regex('Анекдоты'), phrases1),
            MessageHandler(Filters.regex('Калькулятор'), calc1)

            ],
        states={
            gen_key: [MessageHandler(Filters.text, gen2)],
            weather_key: [MessageHandler(Filters.location, weather2)],
            tts_key: [MessageHandler(Filters.text, tts2)],
            calc_key: [MessageHandler(Filters.text, calc2)]
        },
        fallbacks=[CommandHandler('start', start)]
    ))


def main():
    create_log()
    updater = Updater(token= "")
    dispatcher = updater.dispatcher
    set_updaters(dispatcher)
    updater.start_polling()


def start(update, context):
    custom_keyboard = [["Анекдоты", "Калькулятор", "Озвучка голосом"], ["Погода", "Генератор паролей"], ["О создателях"]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    text = "Вы в главном меню"
    update.message.reply_text(text=text, reply_markup=reply_markup)
    return ConversationHandler.END


def gen1(update, context):
    update.message.reply_text(text="Введите количество символов в пароле")
    return gen_key


def gen2(update, context):
    kol = update.message.text
    if kol.isdigit() and int(kol) <= 64:
        pwd = random.sample(' 1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ!@#$%^&*()!@#$%^&*()', int(kol))
        update.message.reply_text(text="".join(pwd))
    else:
        update.message.reply_text("Проверьте введенный текст и повторите попытку)")
    start(update, context)
    return ConversationHandler.END


def weather1(update, context):
    update.message.reply_text(text="Отправьте вашу геолокацию")
    return weather_key


def weather2(update, context):
    txt = update.message
    lat = txt.location.latitude
    lon = txt.location.longitude
    api_key = ""
    request = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=ru")
    response = request.json()

    city = response["name"]
    temperature_now = response["main"]["temp"]
    wind_speed = response["wind"]["speed"]
    weather_description = response["weather"][0]["description"]
    update.message.reply_text(f"Ваш город: {city},\n"
                              f"Погода сейчас: {temperature_now}°C, {weather_description},\n"
                              f"Скорость ветра 🌬: {wind_speed} м/c")

    #update.message.reply_text("Упс, произошла какая-то ошибка 😔")
    return ConversationHandler.END


def phrases1(update, context):
    with open('anek.txt', 'r') as f:
        a = f.read().split('???')
    text = random.choice(a)
    update.message.reply_text(text=text)


def tts1(update, context):
    update.message.reply_text("Отправьте текст, который надо превратить в текст")
    return tts_key


def tts2(update, context):
    txt = update.message.text
    from gtts import gTTS

    def detect_language(text):
        from langdetect import DetectorFactory, detect, detect_langs
        return detect(text)

    myobj = gTTS(text=txt, lang=detect_language(txt), slow=False)
    myobj.save("audio.mp3")
    context.bot.send_audio(chat_id=update.message.from_user.id, audio=open("audio.mp3", "rb"))
    return ConversationHandler.END


def calc1(update, context):
    update.message.reply_text(text="Введите ваше выражение, используя цифры и знаки +, -, /, *, (, ).")
    return calc_key


def calc2(update, context):
    update.message.reply_text(text=eval(update.message.text))
    return ConversationHandler.END


def about(update, context):
    update.message.reply_text(text="О создателях, надо дописать крч")


if __name__ == '__main__':
    main()
