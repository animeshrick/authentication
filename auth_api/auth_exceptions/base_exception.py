from abc import ABC


class TheBaseException(ABC, Exception):
    def __init__(self, msg: str):
        if msg:
            self.msg = msg
