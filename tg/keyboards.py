from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from tg.commands import *


KB_START = ReplyKeyboardMarkup(
    [[CMD_REG, CMD_HELP]],
    one_time_keyboard=False,
    resize_keyboard=True
)
KB_EMPTY = ReplyKeyboardRemove()
KB_MAIN = ReplyKeyboardMarkup(
    [[CMD_ACCOUNT, CMD_HELP]],
    one_time_keyboard=False,
    resize_keyboard=True
)
KB_ACCOUNT = ReplyKeyboardMarkup(
    [[CMD_CHANGE_LOGIN, CMD_CHANGE_PASSWORD],
     [CMD_BACK]],
    one_time_keyboard=False,
    resize_keyboard=True
)
