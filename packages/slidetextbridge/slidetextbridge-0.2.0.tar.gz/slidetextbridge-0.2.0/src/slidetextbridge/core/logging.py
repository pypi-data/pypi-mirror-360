'''
Helper classes and functions to log messages
'''

import logging

class HideSameLogFilter(logging.Filter):
    # pylint: disable=R0903
    '''
    Filter class for logger that removes same log messages
    More precisely, this class saves recent log messages limited by `limit`,
    compares the new message with the saved log messages,
    discard the message if matched.
    '''
    def __init__(self, limit=3):
        super().__init__()
        self._lasts = []
        self._limit = limit

    def filter(self, record):
        for last in self._lasts:
            if last == record.msg:
                return False

        if len(self._lasts) == self._limit:
            self._lasts = self._lasts[1:]
        self._lasts.append(record.msg)

        return True
