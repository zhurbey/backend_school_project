from aiohttp.web import Response

from ..base import BaseView


class Orders(BaseView):
    async def post(self) -> Response:
        pass


class OrdersAssign(BaseView):
    async def post(self) -> Response:
        pass


class OrdersComplete(BaseView):
    async def post(self) -> Response:
        pass
