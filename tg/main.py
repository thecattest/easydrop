import telegram
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import NetworkError, BadRequest

import sqlalchemy

from string import ascii_letters, digits

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
    try:
        tg_user = update.message.from_user
    except AttributeError:
        tg_user = update.callback_query.from_user
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

    if tg_user.username:
    # if len(user_login) > 100 or \
            # not all([letter in ascii_letters + digits + "_-." for letter in user_login]) or \
            # db.query(User).filter(User.login == user_login).first():
        # update.message.reply_text(REG_LOGIN)
        # db.close()
        # return ST_REG_LOGIN
    # else:
        user.login = user_login
        db.commit()
        db.close()
        update.message.reply_text(REG_PASSWORD)
        return ST_REG_PASSWORD
    else:
        db.close()
        update.message.reply_text(REG_LOGIN)
        return ST_REG_LOGIN


def reg_login(update, context):
    user_login = update.message.text
    # if len(user_login) > 100:
        # update.message.reply_text(TOO_LONG)
        # return ST_REG_LOGIN
    # if not all([letter in ascii_letters + digits + "_-." for letter in user_login]):
        # update.message.reply_text(WRONG_CHARACTERS)
        # return ST_REG_LOGIN
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
    # if not all([letter in ascii_letters + digits + "_-." for letter in user_password]):
    #     update.message.reply_text(WRONG_CHARACTERS)
    #     return ST_REG_PASSWORD
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
    db_file.name = file.file_name
    db_file.user_id = db_user.id
    db.add(db_file)
    try:
        db.commit()
        update.message.reply_text(FILE_SAVED)
    except sqlalchemy.exc.DataError as err:
        update.message.reply_text(FILE_NAME_ERROR)
    finally:
        db.close()


def files(update, context, edited=False):
    db = db_session.create_session()
    tg_user, db_user = get_user(update, db)
    files = [(f.name, f.iid) for f in db_user.files]
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(name, callback_data=SHOW + "." + str(iid))]
            for name, iid in files])
    text = FILES_LIST if files else NO_FILES
    if edited:
        files_message_id = context.user_data[FILES_MESSAGE_ID]
        bot.edit_message_text(text, tg_user.id, files_message_id, reply_markup=reply_markup)
    else:
        message = update.message.reply_text(text, reply_markup=reply_markup)
        context.user_data[FILES_MESSAGE_ID] = message.message_id
    db.close()


def file_edit(update, context):
    btn_type, file_id = update.callback_query.data.split(".")
    files_message_id = context.user_data[FILES_MESSAGE_ID]
    db = db_session.create_session()
    tg_user, db_user = get_user(update, db)

    if btn_type == SHOW:
        file = db.query(File).filter(File.iid == int(file_id)).first()
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=RENAME_TEXT, callback_data=RENAME + "." + file_id),
            InlineKeyboardButton(text=DELETE_TEXT, callback_data=DELETE + "." + file_id)]]
        )
        bot.edit_message_text(file.name, tg_user.id, files_message_id, reply_markup=reply_markup)
    elif btn_type == RENAME:
        context.user_data[RENAME] = file_id
        cancel_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(
                text=CMD_CANCEL, callback_data=CMD_CANCEL)
            ]]
        )
        bot.edit_message_text(FILE_RENAME, tg_user.id, files_message_id, reply_markup=cancel_markup)
        db.close()
        return ST_FILE_RENAME
    elif btn_type == DELETE:
        file = db.query(File).filter(File.iid == int(file_id)).first()
        confirmation_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton(text=CMD_YES, callback_data=CMD_YES + "." + file_id),
            InlineKeyboardButton(text=CMD_NO, callback_data=CMD_NO + "." + file_id)
        ]])
        bot.edit_message_text(
            DELETE_CONFIRMATION.format(file.name),
            tg_user.id, files_message_id,
            reply_markup=confirmation_markup)
    elif btn_type == CMD_YES:
        file = db.query(File).filter(File.iid == int(file_id)).first()
        db.delete(file)
        db.commit()
        files(update, context, True)
    elif btn_type == CMD_NO:
        files(update, context, True)
    db.close()


def file_rename(update, context):
    iid = context.user_data[RENAME]
    db = db_session.create_session()
    tg_user, db_user = get_user(update, db)

    file = db.query(File).filter(File.iid == iid).first()
    new_file_name = update.message.text.replace(".", "-") + "." + file.name.split(".")[-1]
    file.name = new_file_name
    db.commit()
    db.close()

    files(update, context, True)
    return ST_MAIN


def file_rename_cancel(update, context):
    files(update, context, True)
    return ST_MAIN


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
    # if len(user_login) > 100:
        # update.message.reply_text(TOO_LONG)
        # return ST_CHANGE_LOGIN
    # if not all([letter in ascii_letters + digits + "_-." for letter in user_login]):
        # update.message.reply_text(WRONG_CHARACTERS)
        # return ST_CHANGE_LOGIN
    # if db_user.login == user_login:
        # update.message.reply_text(LOGIN_SAME, reply_markup=KB_ACCOUNT)
        # return ST_ACCOUNT
    # if db.query(User).filter(User.login == user_login).first():
        # update.message.reply_text(LOGIN_TAKEN)
        # return ST_CHANGE_LOGIN
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
    # if not all([letter in ascii_letters + digits + "_-." for letter in user_password]):
        # update.message.reply_text(WRONG_CHARACTERS)
        # return ST_CHANGE_PASSWORD
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
    entry_points=[MessageHandler(Filters.all, start)],

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
            MessageHandler(Filters.text(CMD_FILES), files),
            MessageHandler(Filters.document, doc),
            CallbackQueryHandler(file_edit)
        ],
        ST_FILE_RENAME: [
            MessageHandler(Filters.regex(".+"), file_rename),
            CallbackQueryHandler(file_rename_cancel)
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
