import json
import typing as t
from datetime import datetime

from aiohttp.web import Response
from asyncpg import Record  # type: ignore

from sweets_store.utils.dates import datetime_to_string, string_to_GMT_datetime

from ..base.views import BaseCreateView, BaseView
from ..bundles.queries import create_bundle, get_courier_active_bundle, update_bundle_status
from ..couriers.queries import get_courier_by_id
from ..orders.queries import (
    get_bundle_not_finished_orders,
    get_order_courier_id,
    is_order_completed,
)
from .datatypes import OrderCreateModel
from .queries import create_orders, get_free_orders, set_order_complete_time
from .utils import filter_orders_for_courier, get_best_orders_subset


# Class aliases should appear at top level:
# https://github.com/python/mypy/issues/9238
ORDERS_VIEW_PARSE_MODEL = OrderCreateModel


class OrdersView(BaseCreateView[ORDERS_VIEW_PARSE_MODEL]):

    PARSE_MODEL = ORDERS_VIEW_PARSE_MODEL

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

        parsing_result = t.cast(t.List[ORDERS_VIEW_PARSE_MODEL], parsing_result)
        created = await create_orders(self.pg, parsing_result)

        ids = [{"id": row["order_id"]} for row in created]
        body = {"orders": ids}

        return Response(body=json.dumps(body), status=201)


class OrdersAssignView(BaseView):
    @staticmethod
    def build_positive_response_body(
        orders: t.List[Record], assign_time: datetime
    ) -> t.Dict[str, t.Any]:

        orders_ids = [order["order_id"] for order in orders]
        body = {
            "orders": [{"id": order_id} for order_id in orders_ids],
            "assign_time": datetime_to_string(assign_time),
        }

        return body

    async def post(self) -> Response:
        request_body = await self.request.json()
        courier_id = request_body.get("courier_id")

        courier = await get_courier_by_id(self.pg, courier_id)
        if not courier:
            return Response(status=400)

        # Check if courier has an active bundle, return not finished orders
        # in response if there is one
        courier_active_bundle_row = await get_courier_active_bundle(self.pg, courier_id)
        if courier_active_bundle_row:
            not_finished_orders = await get_bundle_not_finished_orders(
                self.pg, courier_active_bundle_row["bundle_id"]
            )

            body = self.build_positive_response_body(
                not_finished_orders, courier_active_bundle_row["assign_time"]
            )

            return Response(body=json.dumps(body))

        free_orders = await get_free_orders(self.pg)

        appropriate_orders = filter_orders_for_courier(courier, free_orders)
        best_orders_set = get_best_orders_subset(courier, appropriate_orders)

        if not best_orders_set:
            return Response(body=json.dumps({"orders": []}))

        assign_time = await create_bundle(self.pg, best_orders_set, courier)

        body = self.build_positive_response_body(best_orders_set, assign_time)
        return Response(body=json.dumps(body))


class OrdersCompleteView(BaseView):
    async def post(self) -> Response:
        request_body = await self.request.json()

        order_id = request_body["order_id"]
        courier_id = request_body["courier_id"]
        complete_time = request_body["complete_time"]

        zero_timezone_complete_time = string_to_GMT_datetime(complete_time)
        # get courier_id of courier related to order
        order_courier_id = await get_order_courier_id(self.pg, order_id)

        # Check that there is an order-courier matching pair in database
        if order_courier_id != courier_id:
            return Response(status=400)

        # Check if order is already completed
        order_complete_time = await is_order_completed(self.pg, order_id)
        if order_complete_time:
            return Response(body=json.dumps({"order_id": order_id}))

        updated_order_row = await set_order_complete_time(
            self.pg, order_id, zero_timezone_complete_time
        )

        # Check if bundle is empty after completing this order, mark as completed if so.
        # Do not put this query inside of set_order_complete_time query to avoid circular imports
        await update_bundle_status(self.pg, updated_order_row["bundle_id"])

        return Response(body=json.dumps({"order_id": order_id}))
