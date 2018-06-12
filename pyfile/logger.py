#! code:UTF8 -*-

# logger.py
# A simple logger


def logger(level, who, where, what):
    if level not in ['DEBUG']:
        print((level, who, where, what))
