# -*- encoding: utf-8 -*-
import json
from typing import Any, Callable, Optional

from loguru import logger

from simplejrpc.i18n import T as i18n


# Define the internationalized error message object
class ErrorTextMessage:
    """ """

    def __init__(
        self,
        message: str,
        *args: object,
        translate: Optional[Callable[[str], str]] = None,
    ):
        """ """
        self.message = message
        self.args = args
        self.translate = translate
        self.translate = translate

    def __str__(self) -> str:
        """ """
        try:
            if self.message:
                if self.translate:
                    return self.translate(self.message)
                if not self.args:
                    return i18n.translate(self.message)  # type:ignore
                return i18n.translate_ctx(self.message, *self.args)  # type:ignore
        except Exception as e:
            logger.error(f"ErrorTextMessage: {e}")
            return self.message
        return self.message

    def __repr__(self):
        """ """
        return f"<ErrorTextMessage: {self.message}>"

    def __eq__(self, value: object) -> bool:
        return super().__eq__(value)

    def concat(self, value: object) -> object:
        """ """
        if isinstance(value, str):
            return value + str(self)
        elif isinstance(value, ErrorTextMessage):
            return str(value) + str(self)
        return self

    def __iadd__(self, value: object):
        """ """
        return self.concat(value)

    def __radd__(self, value: object):
        """ """
        return self.concat(value)

    def __add__(self, value: object):
        """ """
        return self.concat(value)


class TextMessageDecoder(json.JSONEncoder):
    """ """

    def default(self, o):
        if isinstance(o, ErrorTextMessage):
            return str(o)
        return o


def json_dumps(obj: Any, **kwargs: Any) -> str:
    """ """
    return json.dumps(obj, cls=TextMessageDecoder, **kwargs)
