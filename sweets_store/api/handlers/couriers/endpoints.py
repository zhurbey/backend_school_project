import json
import typing as t

from aiohttp.web import Response

from ..base.views import BaseCreateView, BaseView
from .datatypes import CourierCreate
from .queries import create_couriers


class CouriersView(BaseCreateView[CourierCreate]):

    PARSE_MODEL = CourierCreate

    async def post(self) -> Response:
        request_body = await self.request.json()
        data = request_body.get("data", [])

        # if have_parsing_errors is true, parsing_result is errors reports, otherwise it's a
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

        parsing_result = t.cast(t.List[CourierCreate], parsing_result)
        created = await create_couriers(self.pg, parsing_result)

        ids = [{"id": row["courier_id"]} for row in created]
        body = {"couriers": ids}

        return Response(body=json.dumps(body), status=201)


class CourierView(BaseView):
    async def patch(self) -> Response:
        pass

    async def get(self) -> Response:
        pass
