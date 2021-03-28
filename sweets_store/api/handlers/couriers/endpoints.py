import json
import typing as t

from aiohttp.web import Response

from ..base.views import BaseCreateView
from ..bundles.queries import get_courier_active_bundle, release_orders
from ..orders.queries import get_bundle_not_finished_orders
from ..orders.utils import filter_orders_for_courier, get_best_orders_subset
from .datatypes import CourierCreateModel, CourierPatchModel
from .queries import (
    create_couriers,
    get_aggregated_bundles_for_courier,
    get_courier_by_id,
    get_courier_finished_bundles,
    update_courier,
)
from .utils import (
    calculate_courier_earnings,
    calculate_courier_rating,
    get_best_region_average_time,
)


# Class aliases should appear at top level:
# https://github.com/python/mypy/issues/9238
COURIERS_VIEW_PARSE_MODEL = CourierCreateModel


class CouriersView(BaseCreateView[COURIERS_VIEW_PARSE_MODEL]):

    PARSE_MODEL = COURIERS_VIEW_PARSE_MODEL

    async def post(self) -> Response:
        request_body = await self.request.json()
        data = request_body.get("data", [])

        # if have_parsing_errors is true - parsing_result is errors reports, otherwise it's a
        # list of parsed couriers
        have_parsing_errors, parsing_result = self.parse_data(data, "courier_id")

        if have_parsing_errors:
            # redefine variable below, don't need to bind type
            body: t.Any = {
                "validation_error": {
                    "couriers": [{"id": courier_id} for courier_id in parsing_result],
                    **parsing_result,  # type: ignore
                }
            }

            return Response(body=json.dumps(body), status=400)

        parsing_result = t.cast(t.List[COURIERS_VIEW_PARSE_MODEL], parsing_result)
        created_couriers = await create_couriers(self.pg, parsing_result)

        ids = [{"id": row["courier_id"]} for row in created_couriers]
        body = {"couriers": ids}

        return Response(body=json.dumps(body), status=201)


class CourierView(BaseCreateView[CourierPatchModel]):

    PARSE_MODEL = CourierPatchModel

    @property
    def courier_id(self) -> int:
        return int(self.request.match_info.get("courier_id"))  # type: ignore

    async def patch(self) -> Response:
        request_body = await self.request.json()

        # if have_parsing_errors is true - parsing_result is errors reports, otherwise it's a
        # list, containing parsed data object
        have_parsing_errors, parsing_result = self.parse_data([request_body], "courier_id")

        if have_parsing_errors:
            return Response(body=json.dumps(parsing_result), status=400)

        # Filter fields with None values(Ones that were not provided in request)
        filtered_fields = {}
        for key, value in parsing_result[0].dict().items():
            if value is not None:
                filtered_fields[key] = value

        patched_courier_row = await update_courier(self.pg, filtered_fields)

        active_bundle = await get_courier_active_bundle(self.pg, patched_courier_row["courier_id"])
        # If courier doesn't have active bundle - just return updated courier data
        if not active_bundle:
            return Response(body=json.dumps(dict(patched_courier_row)))

        # Filter orders which are not appropriate for this courier now, take optimal subset
        not_finished_orders = await get_bundle_not_finished_orders(
            self.pg, active_bundle["bundle_id"]
        )
        filtered_orders = filter_orders_for_courier(patched_courier_row, not_finished_orders)
        best_orders_subset = get_best_orders_subset(patched_courier_row, filtered_orders)

        not_appropriate_orders_ids = []  # orders list which courier can't carry after patch
        for row in not_finished_orders:
            if row not in best_orders_subset:
                not_appropriate_orders_ids.append(row["order_id"])

        # Mark orders that doesn't fit for courier as free ones and close courier's bundle if empty
        await release_orders(self.pg, not_appropriate_orders_ids, active_bundle["bundle_id"])

        return Response(body=json.dumps(dict(patched_courier_row)))

    async def get(self) -> Response:
        courier_row = await get_courier_by_id(self.pg, self.courier_id)
        courier_data = dict(courier_row)  # type: ignore

        # If there's no finished_bundles for courier - earning = 0, rating is not defined
        finished_bundles = await get_courier_finished_bundles(self.pg, courier_data["courier_id"])
        if not finished_bundles:
            courier_data["earnings"] = 0
            return Response(body=json.dumps(courier_data))

        bundles_aggregations = await get_aggregated_bundles_for_courier(self.pg, self.courier_id)
        t_constant = get_best_region_average_time(bundles_aggregations)

        courier_data["rating"] = calculate_courier_rating(t_constant)
        courier_data["earning"] = calculate_courier_earnings(finished_bundles)

        return Response(body=json.dumps(courier_data))
