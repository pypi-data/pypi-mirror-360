import asyncio
import os
import sys
import unittest

from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from simplejrpc.app import ServerApplication
from simplejrpc.config import DEFAULT_LOGGING_CONFIG
from simplejrpc.i18n import GI18n, Language, T
from simplejrpc.interfaces import RPCMiddleware
from simplejrpc.response import jsonify

# from simplejrpc.schemas import BaseForm, StrRangeValidator, simple


# # Test-form
# class TestForm(BaseForm):
#     """ """

#     action = simple.StringField(
#         validators=[StrRangeValidator(allows=["start", "stop"])]
#     )


# Test-middleware
class CustomMiddleware(RPCMiddleware):
    """ """

    def process_request(self, request, context):
        print("[middleware-request] ", request, context)
        return request

    def process_response(self, response, context):
        print("[middleware-response] ", response, context)
        return response


current_path = os.path.dirname(__file__)
socket_path = os.path.join(current_path, "tmp.socket")
pid_path = os.path.join(current_path, "tmp.pid")


app = ServerApplication(socket_path, config_path=DEFAULT_LOGGING_CONFIG)
app.middleware(CustomMiddleware())


@app.route(name="hello")
async def hello(lang, action):
    """ """
    # raise RPCException("1111111")
    print(T.translate("1111"))
    return jsonify(data=[1, 2, 3], msg="OK")


class TestApp(unittest.TestCase):
    """ """

    # @unittest.skip
    def test_app(self):
        """ """
        lang_path = os.path.join(current_path, "i18n")
        GI18n(lang_path, lang=Language.EN)
        # app.run_daemon()
        asyncio.run(app.run(daemon=False, fpidfile=pid_path))
        # app.run_sync()
        print("Server started")

    @unittest.skip
    def test_i18n(self):
        """ """
        lang_path = os.path.join(current_path, "i18n")
        GI18n(lang_path, lang=Language.EN)

    @unittest.skip
    def test_logger(self):
        """ """
        logger.info("---111111111")


if __name__ == "__main__":
    """ """
    unittest.main()
