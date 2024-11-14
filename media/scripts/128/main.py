from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, Updater, CommandHandler


TOKEN = '7915736407:AAHU4R-1LDgwBag5IbdijDntQOjDPYRVyq8'
bot = Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)


topic_ids = {
    'button1': '5269410357',
    'button2': '5269410357',
    'button3': '5269410357'
}


def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Taklif", callback_data='button1')],
        [InlineKeyboardButton("Shikoyat", callback_data='button2')],
        [InlineKeyboardButton("Murojaat", callback_data='button3')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Bu sizning yuborayotgan xabaringiz', reply_markup=reply_markup)


def button_callback(update, context):
    query = update.callback_query
    query.answer()

    button_data = query.data
    topic_id = topic_ids.get(button_data)


    if topic_id:
        message = f'{button_data} tugmasi bosildi. Bu {button_data} uchun ma\'lumot!'
        bot.send_message(chat_id=topic_id, text=message)
        query.edit_message_text(text=f"{button_data} tugmasi bosildi, ma'lumot yuborildi!")


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CallbackQueryHandler(button_callback))


updater.start_polling()
updater.idle()
