import telegram
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, ConversationHandler
from telegram import Bot
from telegram.error import NetworkError

from string import ascii_lowercase

from tg.commands import *
from tg.strings import *
from tg.keyboards import *

from db_init import *


try:
    from tg.tg_token import TOKEN, CHAT_ID
except ImportError:
    raise ImportError('Telegram config file not found')


def get_user(update, db):
    tg_user = update.message.from_user
    db_user = db.query(User).filter(User.id == tg_user.id).first()
    return tg_user, db_user


def start(update, context):
    db = db_session.create_session()
    tg_user, db_user = get_user(update, db)
    db.close()
    if db_user:
        update.message.reply_text(HELLO, reply_markup=KB_MAIN)
        return ST_MAIN
    else:
        update.message.reply_text(HELLO, reply_markup=KB_START)
    return ST_REG


def help(update, context):
    update.message.reply_text(HELP)


def default(update, context):
    update.message.reply_text(DEFAULT)


def reg(update, context):
    db = db_session.create_session()
    tg_user, _ = get_user(update, db)
    user = User()
    user.id = tg_user.id
    user.login = tg_user.username if tg_user.username else tg_user.id
    db.add(user)
    db.commit()
    db.close()
    update.message.reply_text(REG_START, reply_markup=KB_EMPTY)
    return ST_PASSWORD


def password(update, context):
    user_password = update.message.text
    db = db_session.create_session()
    tg_user, db_user = get_user(update, db)
    db_user.set_password(user_password)
    db.commit()
    update.message.reply_text(CREDENTIALS.format(db_user.login, user_password))
    update.message.reply_text(REG_SUCCESS, reply_markup=KB_MAIN)
    db.close()
    return ST_MAIN


def account(update, context):
    update.message.reply_text(ACCOUNT, reply_markup=KB_ACCOUNT)
    return ST_ACCOUNT


def account_login(update, context):
    update.message.reply_text(ACCOUNT_LOGIN_CHANGE, reply_markup=KB_EMPTY)
    return ST_ACCOUNT_LOGIN


def change_login(update, context):
    db = db_session.create_session()
    user_login = update.message.text
    tg_user, db_user = get_user(update, db)
    if len(user_login) > 100:
        update.message.reply_text()
        return ST_ACCOUNT_LOGIN
    if not all([letter in ascii_lowercase for letter in user_login]):
        update.message.reply_text(ACCOUNT_LOGIN_CHANGE_WRONG_CHARACTERS)
        return ST_ACCOUNT_LOGIN
    if db_user.login == user_login:
        update.message.reply_text(ACCOUNT_LOGIN_CHANGE_LOGIN_SAME)
        return ST_ACCOUNT_LOGIN
    if db.query(User).filter(User.login == user_login).first():
        update.message.reply_text(ACCOUNT_LOGIN_CHANGE_LOGIN_TAKEN)
        return ST_ACCOUNT_LOGIN
    db_user.login = user_login
    db.commit()
    db.close()
    update.message.reply_text(ACCOUNT_LOGIN_CHANGE_SUCCESS, reply_markup=KB_MAIN)
    return ST_MAIN


def account_password(update, context):
    update.message.reply_text(ACCOUNT_PASSWORD_CHANGE, reply_markup=KB_EMPTY)
    return ST_ACCOUNT_PASSWORD


def change_password(update, context):
    db = db_session.create_session()
    user_password = update.message.text
    tg_user, db_user = get_user(update, db)
    db_user.set_password(user_password)
    db.commit()
    db.close()
    update.message.reply_text(ACCOUNT_PASSWORD_CHANGE_SUCCESS, reply_markup=KB_MAIN)
    return ST_MAIN


def back(update, context):
    update.message.reply_text(CMD_BACK, reply_markup=KB_MAIN)
    return ST_MAIN


updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex('.*'), start)],

    states={
        ST_REG: [
            MessageHandler(Filters.text(CMD_REG), reg)
        ],
        ST_PASSWORD: [
            MessageHandler(Filters.regex('.+'), password)
        ],
        ST_MAIN: [
            MessageHandler(Filters.text(CMD_ACCOUNT), account)
        ],
        ST_ACCOUNT: [
            MessageHandler(Filters.text(CMD_CHANGE_LOGIN), account_login),
            MessageHandler(Filters.text(CMD_CHANGE_PASSWORD), account_password),
            MessageHandler(Filters.text(CMD_BACK), back)
        ],
        ST_ACCOUNT_LOGIN: [
            MessageHandler(Filters.regex('.+'), change_login)
        ],
        ST_ACCOUNT_PASSWORD: [
            MessageHandler(Filters.regex('.+'), change_password)
        ]

    },

    fallbacks=[MessageHandler(Filters.text(CMD_HELP), help), MessageHandler(Filters.all, default)]
)
dp.add_handler(conversation_handler)
bot = updater.bot

if __name__ == '__main__':
    updater.start_polling()
    updater.idle()
