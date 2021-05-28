from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from tg.commands import *


KB_START = ReplyKeyboardMarkup(
    [[CMD_REG, CMD_HELP]],
    one_time_keyboard=False,
    resize_keyboard=True
)
KB_REG = ReplyKeyboardRemove()
KB_PASSWORD = ReplyKeyboardMarkup(
    [[CMD_ACCOUNT, CMD_HELP]],
    one_time_keyboard=False,
    resize_keyboard=True
)
