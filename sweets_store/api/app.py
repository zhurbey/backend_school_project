from aiohttp import web

from .handlers.couriers.endpoints import get_courier, patch_courier, post_couriers
from .handlers.orders.endpoints import assign_order, complete_order, post_orders


app = web.Application()

app.add_routes(
    [
        web.post("/couriers", post_couriers),
        web.patch("/couriers/{courier_id}", patch_courier),
        web.get("/couriers/{courier_id}", get_courier),
        web.post("/orders", post_orders),
        web.post("/orders/assign", assign_order),
        web.post("/orders/complete", complete_order),
    ]
)


def start_server() -> None:

    web.run_app(app)
