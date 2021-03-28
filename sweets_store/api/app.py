from aiohttp import web

from sweets_store.db.engine import connect_db, disconnect_db

from .handlers.couriers.endpoints import CourierView, CouriersView
from .handlers.orders.endpoints import OrdersAssignView, OrdersCompleteView, OrdersView


app = web.Application()

app.add_routes(
    [
        web.post("/couriers", CouriersView),
        web.patch("/couriers/{courier_id}", CourierView),
        web.get("/couriers/{courier_id}", CourierView),
        web.post("/orders", OrdersView),
        web.post("/orders/assign", OrdersAssignView),
        web.post("/orders/complete", OrdersCompleteView),
    ]
)


def start_server() -> None:

    app.on_startup.append(connect_db)
    app.on_cleanup.append(disconnect_db)

    web.run_app(app)
