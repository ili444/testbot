# -*- coding: utf-8 -*-
from enum import Enum

token = '696434286:AAGtH9kExLEAiX4m1eUl2CyM1MBkUmcqWco'
db_file = "database.vdb"


class States(Enum):
    S_START = "0"  # Начало нового диалога
    S_wait = "1"
    S_type_print = "2"
