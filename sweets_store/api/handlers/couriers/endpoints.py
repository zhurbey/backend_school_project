import json

from aiohttp.web import Response
from pydantic import ValidationError
from asyncpg.exceptions import UniqueViolationError

from ..base import BaseView
from .datatypes import CourierCreate
from .queries import create_couriers


class CouriersView(BaseView):

    async def post(self) -> Response:
        request_body = await self.request.json()
        data = request_body.get("data", [])

        parsing_errors = []
        parsed_couriers = []

        for courier in data:

            try:
                parsed_couriers.append(CourierCreate(**courier))
            except ValidationError as error:
                # parsing_errors.append((list_index, error.json()))
                parsing_errors.append(courier['courier_id'])

        if parsing_errors:
            body = {
                "validation_error": {
                    "couriers": [{"id": courier_id} for courier_id in parsing_errors]
                }
            }

            return Response(body=json.dumps(body), status=400)

        # There's already a row with id of one of new couriers
        try:
            created = await create_couriers(self.pg, parsed_couriers)
        except UniqueViolationError as error:
            return Response(body=json.dumps({error: "Unique id constraint violation"}), status=400)

        ids = [{"id": row["courier_id"]} for row in created]
        body = {"couriers": ids}

        return Response(body=json.dumps(body), status=201)


class CourierView(BaseView):
    async def patch(self) -> Response:
        pass

    async def get(self) -> Response:
        pass
