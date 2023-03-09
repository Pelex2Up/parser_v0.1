import telebot


bot = telebot.TeleBot('6068350064:AAHsBxFlFSqkbjZ2Hkv6Touh8iIpC_V6HLM')
REPORT_GROUP_ID = -723121616


def send_tg_post(message):
    bot.send_message(REPORT_GROUP_ID, message, parse_mode='html')
