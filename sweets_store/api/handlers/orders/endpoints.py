import json
import typing as t
from datetime import datetime

from aiohttp.web import Response
from asyncpg import Record  # type: ignore

from sweets_store.utils.dates import datetime_to_string

from ..base.views import BaseCreateView, BaseView
from ..bundles.queries import create_bundle, get_courier_active_bundle
from ..couriers.queries import get_courier_by_id
from ..orders.queries import get_bundle_not_finished_orders
from .datatypes import OrderCreate
from .queries import create_orders, get_free_orders
from .utils import filter_orders_for_courier, get_best_orders_subset


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
    @staticmethod
    def make_positive_response_body(
        orders: t.List[Record], assign_time: datetime
    ) -> t.Dict[str, t.Any]:

        orders_ids = [order["order_id"] for order in orders]
        assign_time_str = datetime_to_string(assign_time)
        body = {
            "orders": [{"id": order_id} for order_id in orders_ids],
            "assign_time": assign_time_str,
        }

        return body

    async def post(self) -> Response:
        request_body = await self.request.json()
        courier_id = request_body.get("courier_id")

        courier = await get_courier_by_id(self.pg, courier_id)
        if not courier:
            return Response(status=400)

        # Check if courier has active bundle, return not finished orders
        # in response if there is one
        courier_active_bundle = await get_courier_active_bundle(self.pg, courier_id)
        if courier_active_bundle:
            not_finished_orders = await get_bundle_not_finished_orders(
                self.pg, courier_active_bundle["bundle_id"]
            )

            body = self.make_positive_response_body(
                not_finished_orders, courier_active_bundle["assign_time"]
            )

            return Response(body=json.dumps(body))

        free_orders = await get_free_orders(self.pg)

        appropriate_orders = filter_orders_for_courier(courier, free_orders)
        best_orders_set = get_best_orders_subset(courier, appropriate_orders)

        if not best_orders_set:
            return Response(body=json.dumps({"orders": []}))

        assign_time = await create_bundle(self.pg, courier, best_orders_set)
        body = self.make_positive_response_body(best_orders_set, assign_time)
        return Response(body=json.dumps(body))


class OrdersComplete(BaseView):
    async def post(self) -> Response:
        pass
