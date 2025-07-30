import asyncio
import os
import sys
import unittest

# from jsonrpcclient import request, parse

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


current_path = os.path.dirname(__file__)
socket_path = os.path.join(current_path, "tmp.socket")

SOCKET_PATH = socket_path

from simplejrpc.client import GmSyncRpcClient, Request


class TestJsonRpc(unittest.TestCase):
    """ """

    @unittest.skip
    def test_hello(self):
        """ """
        method = "hello"
        params = {"lang": "zh-CN", "action": "start"}

        # params = {}
        request = Request(socket_path)

        async def run_session():
            # session.send_message(method, params)
            return await request.send_request(method, params)

        result = asyncio.run(run_session())
        print("[recv] > ", result)

    @unittest.skip
    def test_hello(self):
        """ """
        method = "hello"
        params = {"lang": "zh-CN", "action": "start"}
        request = Request(socket_path)
        result = request.send_request(method, params)
        print("[recv] > ", result)

    def test_hello1(self):
        """ """
        method = "hello"
        params = {"lang": "zh-CN", "action": "start"}
        request = Request(adapter=GmSyncRpcClient(socket_path))
        result = request.send_request(method, params)
        print("[recv] > ", result)


if __name__ == "__main__":
    unittest.main()
