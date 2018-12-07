# -*- coding: utf-8 -*-
from enum import Enum
import os
TOKEN = os.environ['token']



class States(Enum):
    S_START = "0"  # Начало нового диалога
    S_wait = "1"
    S_type_print = "2"
