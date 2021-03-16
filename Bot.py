import telebot
from telebot import types
from config import TOKEN
import cash
import parsing

bot = telebot.TeleBot(TOKEN)


# Обрабатываются все сообщения содержащие команды '/start' or '/help'.
@bot.message_handler(commands=['start'])
def handle_start(message):
    options_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    opt_mark_button1 = types.KeyboardButton('Конвертация')
    opt_mark_button2 = types.KeyboardButton('Курс валют')
    opt_mark_button3 = types.KeyboardButton('Инструкция')
    options_markup.add(opt_mark_button1, opt_mark_button2, opt_mark_button3)

    bot.send_sticker(message.chat.id, open('static/join.webp', 'rb'))
    bot.send_message(message.chat.id, "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>"
                                      " узнаванию курса валют  😉".format(message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=options_markup)


@bot.message_handler(commands=['add'])
def handle_add(message):
    bot.send_message(message.chat.id, 'Что бы добавить валюту напишите её сокращение, например:"ils, usd, eur, rub".')


@bot.message_handler(content_types=['text'])
def conversion(message):
    if message.chat.type == 'private':
        try:
            if message.text == 'Конвертация':
                markup = types.InlineKeyboardMarkup(row_width=1)
                for i in cash.get_currency():
                    markup.add(types.InlineKeyboardButton(i[1], callback_data='&' + i[1] + i[0]))  # first currency
                bot.send_message(message.chat.id, 'Из какой валюты перевести?', reply_markup=markup)
                return
            elif message.text == 'Курс валют':
                markup = types.InlineKeyboardMarkup(row_width=1)
                for i in cash.get_currency():
                    markup.add(types.InlineKeyboardButton(i[1], callback_data='(' + i[1] + i[0]))  # first currency
                bot.send_message(message.chat.id, 'В какой валюте вы хотите узнать курс?', reply_markup=markup)
            elif message.text == 'Инструкция':
                bot.send_message(message.chat.id, '<b>Что же умеет этот бот?🤔</b>\nТа всё обуснено в командах.😉\n'
                                                  'Единственная скрытая функция это добавление новых валют в систему,'
                                                  ' просто пишете сокращение валюты которую хотите добавить к примеру:'
                                                  ' "usd" или "rub"(Валюты находяшаяся в системе нет смысла писать)\n'
                                                  '<b>Удачи в использовании!</b>😏', parse_mode='html')
                bot.send_sticker(message.chat.id, open('static/instructions.webp', 'rb'))
            elif 0 < int(message.text): # не может быть выше потому что после будет исключение.
                first, second = cash.get_two_currency(message.chat.id)
                bot.send_message(message.chat.id, str(message.text) + first[:-3].replace('/', ' ')
                                 + second[:-3].replace('/', ' в ') + ' получается '
                                 + str(parsing.get_price(first.replace(first[:-3], ''),
                                                         second.replace(second[:-3], ''), message.text)[
                                           0]) + '.')
                return
        except ValueError:
            if len(message.text) == 3:
                if cash.add_currency(message.text):
                    bot.send_message(message.chat.id, 'Валюта успешно добавленна.')
                else:
                    bot.send_message(message.chat.id, 'Либо такой валюты немае в природе либо она уже есть.')
            else:
                bot.send_message(message.chat.id, 'Простите я вас не понимаю.')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.data[0] == '(':
            callback_values = "Валюты находящаяся в системе в переводе на " + call.data[:-3].replace('(', '') + ':\n'
            count = 1
            for i in parsing.get_values(call.data.replace(call.data[:-3], '')):
                callback_values += str(count) + '. ' + i[1] + ': ' + i[0] + '.\n'
                count += 1
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=callback_values, reply_markup=None)
        elif call.data[0] == '&':  # first currency
            currency = call.data[:-3].replace(call.data[0], '')
            cash.conversion_help(call.data, call.message.chat.id, 1)
            markup = types.InlineKeyboardMarkup(row_width=1)
            for i in cash.get_currency():
                if i[1] != currency:
                    markup.add(types.InlineKeyboardButton(i[1], callback_data='%' + i[1] + i[0]))  # second currency
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='В какую валюту вы хотите перевести ' + currency + '?', reply_markup=markup)
        elif call.data[0] == '%':
            currency = call.data[:-3].replace(call.data[0], '')
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(types.InlineKeyboardButton('10', callback_data=10),
                       types.InlineKeyboardButton('50', callback_data=50),
                       types.InlineKeyboardButton('100', callback_data=100),
                       types.InlineKeyboardButton('500', callback_data=500),
                       types.InlineKeyboardButton('1000', callback_data=1000))
            # Да тут можно было сделать при помощи редис с возможностью добавления величин без входа в код.
            cash.conversion_help(call.data, call.message.chat.id, 0)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Значит ' + cash.get_first(call.message.chat.id)[:-3]
                                  .replace(cash.get_first(call.message.chat.id)[0], '') + ' в '
                                       + currency + ', но сколько?\nВы так же можете ввести Ваше число (целое).',
                                  reply_markup=markup)
        elif 0 < int(call.data):
            first, second = cash.get_two_currency(call.message.chat.id)
            print(first[:-3].replace('/', ' ')
                  + second[:-3].replace('/', '  '))
            print(second.replace(second[:-3], ''))
            bot.send_message(call.message.chat.id, str(call.data) + first[:-3].replace('/', ' ')
                             + second[:-3].replace('/', ' в ') + ' получается '
                             + 'будет ' + str(parsing.get_price(first.replace(first[:-3], ''),
                                                                second.replace(second[:-3], ''), call.data)[0]) + '.')
    except ValueError or Exception as e:
        print(repr(e))


@bot.message_handler(content_types=['voice'])
def handle_docs_audio(message: telebot.types.Message):
    bot.send_message(message.chat.id, 'message')


# Обрабатывается все документы и аудиозаписи
@bot.message_handler(content_types=['document', 'audio'])
def handle_docs_audio(message):
    bot.send_message(message.chat.id, 'something')


@bot.message_handler(content_types=['photo'])
def handle_docs_audio(message):
    bot.send_message(message.chat.id, 'nice meme XDD')


bot.polling(none_stop=True)
