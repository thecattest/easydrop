import telegram
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, ConversationHandler
from telegram import Bot
from telegram.error import NetworkError

from tg.commands import *
from tg.strings import *
from tg.keyboards import *


try:
    from tg.tg_token import TOKEN, CHAT_ID
except ImportError:
    raise ImportError('Telegram config file not found')


def start(update, context):
    update.message.reply_text(HELLO, reply_markup=KB_START)
    return ST_REG


def help(update, context):
    update.message.reply_text(HELP)


def default(update, context):
    update.message.reply_text(DEFAULT)


def reg(update, context):
    update.message.reply_text(LOGIN, reply_markup=KB_REG)
    return ST_LOGIN


def login(update, context):
    user_login = update.message.text
    update.message.reply_text("твой логин: " + user_login)
    update.message.reply_text(PASSWORD)
    return ST_PASSWORD


def password(update, context):
    user_password = update.message.text
    update.message.reply_text("твой пароль: " + user_password)
    update.message.reply_text(MAIN, reply_markup=KB_PASSWORD)
    return ST_MAIN


def account(update, context):
    update.message.reply_text(ACCOUNT)


updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex('.*'), start)],

    states={
        ST_REG: [
            MessageHandler(Filters.text(CMD_REG), reg)
        ],
        ST_LOGIN: [
            MessageHandler(Filters.regex('.+'), login)
        ],
        ST_PASSWORD: [
            MessageHandler(Filters.regex('.+'), password)
        ],
        ST_MAIN: [
            MessageHandler(Filters.text(CMD_ACCOUNT), account)
        ]
    },

    fallbacks=[MessageHandler(Filters.text(CMD_HELP), help), MessageHandler(Filters.all, default)]
)
dp.add_handler(conversation_handler)
bot = updater.bot

if __name__ == '__main__':
    updater.start_polling()
    updater.idle()
