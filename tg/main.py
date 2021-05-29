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
    with open("tg/tg_config") as f:
        TOKEN = f.readline()
except FileNotFoundError:
    raise FileNotFoundError("Telegram config file not found")


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
        help(update, context)
    return ST_REG


def help(update, context):
    update.message.reply_text(HELP)


def default(update, context):
    update.message.reply_text(DEFAULT)


def reg(update, context):
    update.message.reply_text(REG, reply_markup=KB_EMPTY)
    db = db_session.create_session()
    tg_user, _ = get_user(update, db)

    user = User()
    user.id = tg_user.id
    user.hashed_password = ""
    db.add(user)
    db.commit()

    user_login = tg_user.username if tg_user.username else tg_user.id
    if len(user_login) > 100 or \
            not all([letter in ascii_lowercase for letter in user_login]) or \
            db.query(User).filter(User.login == user_login).first():
        update.message.reply_text(REG_LOGIN)
        db.close()
        return ST_REG_LOGIN
    else:
        user.login = user_login
        db.commit()
        db.close()
        update.message.reply_text(REG_PASSWORD)
        return ST_REG_PASSWORD


def reg_login(update, context):
    user_login = update.message.text
    if len(user_login) > 100:
        update.message.reply_text(TOO_LONG)
        return ST_REG_LOGIN
    if not all([letter in ascii_lowercase for letter in user_login]):
        update.message.reply_text(WRONG_CHARACTERS)
        return ST_REG_LOGIN
    db = db_session.create_session()
    tg_user, db_user = get_user(update, db)
    if db.query(User).filter(User.login == user_login).first():
        update.message.reply_text(LOGIN_TAKEN)
        return ST_REG_LOGIN
    db_user.login = user_login
    db.commit()
    db.close()
    update.message.reply_text(REG_PASSWORD)
    return ST_REG_PASSWORD


def reg_password(update, context):
    user_password = update.message.text
    if not all([letter in ascii_lowercase for letter in user_password]):
        update.message.reply_text(WRONG_CHARACTERS)
        return ST_REG_PASSWORD
    db = db_session.create_session()
    tg_user, db_user = get_user(update, db)
    db_user.set_password(user_password)
    db.commit()
    update.message.reply_text(CREDENTIALS.format(db_user.login, user_password))
    update.message.reply_text(REG_SUCCESS, reply_markup=KB_MAIN)
    db.close()
    return ST_MAIN


def doc(update, context):
    file = update.message.document
    db = db_session.create_session()
    _, db_user = get_user(update, db)
    db_file = File()
    db_file.id = file.file_id
    db_file.name = file.file_name.replace(" ", "_")
    db_file.user_id = db_user.id
    db.add(db_file)
    db.commit()
    db.close()
    update.message.reply_text(FILE_SAVED)


def account(update, context):
    db = db_session.create_session()
    _, db_user = get_user(update, db)
    db.close()
    update.message.reply_text(ACCOUNT_SETTINGS.format(db_user.login), reply_markup=KB_ACCOUNT)
    return ST_ACCOUNT


def account_login(update, context):
    update.message.reply_text(NEW_LOGIN, reply_markup=KB_BACK)
    return ST_CHANGE_LOGIN


def change_login(update, context):
    db = db_session.create_session()
    user_login = update.message.text
    tg_user, db_user = get_user(update, db)
    if len(user_login) > 100:
        update.message.reply_text(TOO_LONG)
        return ST_CHANGE_LOGIN
    if not all([letter in ascii_lowercase for letter in user_login]):
        update.message.reply_text(WRONG_CHARACTERS)
        return ST_CHANGE_LOGIN
    if db_user.login == user_login:
        update.message.reply_text(LOGIN_SAME, reply_markup=KB_ACCOUNT)
        return ST_ACCOUNT
    if db.query(User).filter(User.login == user_login).first():
        update.message.reply_text(LOGIN_TAKEN)
        return ST_CHANGE_LOGIN
    db_user.login = user_login
    db.commit()
    db.close()
    update.message.reply_text(LOGIN_CHANGE_SUCCESS, reply_markup=KB_MAIN)
    return ST_MAIN


def account_password(update, context):
    update.message.reply_text(NEW_PASSWORD, reply_markup=KB_BACK)
    return ST_CHANGE_PASSWORD


def change_password(update, context):
    user_password = update.message.text
    if not all([letter in ascii_lowercase for letter in user_password]):
        update.message.reply_text(WRONG_CHARACTERS)
        return ST_CHANGE_PASSWORD
    db = db_session.create_session()
    tg_user, db_user = get_user(update, db)
    db_user.set_password(user_password)
    db.commit()
    db.close()
    update.message.reply_text(PASSWORD_CHANGE_SUCCESS, reply_markup=KB_MAIN)
    return ST_MAIN


def account_delete(update, context):
    update.message.reply_text(ACCOUNT_DELETE, reply_markup=KB_ACCOUNT_DELETE)
    return ST_DELETE_ACCOUNT


def delete(update, context):
    db = db_session.create_session()
    _, db_user = get_user(update, db)
    db.delete(db_user)
    db.commit()
    db.close()
    update.message.reply_text("отныне я не знаю тебя...", reply_markup=KB_DEFAULT)
    return ConversationHandler.END


def back(update, context):
    update.message.reply_text(CMD_BACK, reply_markup=KB_MAIN)
    return ST_MAIN


def cancel(update, context):
    return account(update, context)


updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex('.*'), start)],

    states={
        ST_REG: [
            MessageHandler(Filters.text(CMD_REG), reg)
        ],
        ST_REG_LOGIN: [
            MessageHandler(Filters.regex('.+'), reg_login)
        ],
        ST_REG_PASSWORD: [
            MessageHandler(Filters.regex('.+'), reg_password)
        ],
        ST_MAIN: [
            MessageHandler(Filters.text(CMD_ACCOUNT), account),
            MessageHandler(Filters.document, doc)
        ],
        ST_ACCOUNT: [
            MessageHandler(Filters.text(CMD_CHANGE_LOGIN), account_login),
            MessageHandler(Filters.text(CMD_CHANGE_PASSWORD), account_password),
            MessageHandler(Filters.text(CMD_DELETE_ACCOUNT), account_delete),
            MessageHandler(Filters.text(CMD_BACK), back)
        ],
        ST_CHANGE_LOGIN: [
            MessageHandler(Filters.text(CMD_CANCEL), cancel),
            MessageHandler(Filters.regex('.+'), change_login)
        ],
        ST_CHANGE_PASSWORD: [
            MessageHandler(Filters.text(CMD_CANCEL), cancel),
            MessageHandler(Filters.regex('.+'), change_password)
        ],
        ST_DELETE_ACCOUNT: [
            MessageHandler(Filters.text(CMD_YES), delete),
            MessageHandler(Filters.text(CMD_NO), back),
        ]

    },

    fallbacks=[MessageHandler(Filters.text(CMD_HELP), help), MessageHandler(Filters.all, default)]
)
dp.add_handler(conversation_handler)
bot = updater.bot
