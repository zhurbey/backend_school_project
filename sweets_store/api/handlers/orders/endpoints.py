import json
import typing as t

from aiohttp.web import Response

from ..base import BaseCreateView, BaseView
from .datatypes import OrderCreate
from .queries import create_orders


class Orders(BaseCreateView[OrderCreate]):

    PARSE_MODEL = OrderCreate

    async def post(self) -> Response:
        request_body = await self.request.json()
        data = request_body.get("data", [])

        # if have_parsing_errors is true, parsing_result is errors reports, otherwise it's a
        # list of parsed orders
        have_parsing_errors, parsing_result = self.parse_data(data, "order_id")

        if have_parsing_errors:
            # redefine variable below, don't need to bind type
            body: t.Any = {
                "validation_error": {
                    "orders": [{"id": order_id} for order_id in parsing_result],
                    **parsing_result,  # type: ignore
                }
            }

            return Response(body=json.dumps(body), status=400)

        parsing_result = t.cast(t.List[OrderCreate], parsing_result)
        created = await create_orders(self.pg, parsing_result)

        ids = [{"id": row["order_id"]} for row in created]
        body = {"orders": ids}

        return Response(body=json.dumps(body), status=201)


class OrdersAssign(BaseView):
    async def post(self) -> Response:
        pass


class OrdersComplete(BaseView):
    async def post(self) -> Response:
        pass
