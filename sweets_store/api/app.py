from aiohttp import web

from sweets_store.db.engine import connect_db, disconnect_db

from .handlers.couriers.endpoints import CourierView, CouriersView
from .handlers.orders.endpoints import Orders, OrdersAssign, OrdersComplete


app = web.Application()

app.add_routes(
    [
        web.post("/couriers", CouriersView),
        web.patch("/couriers/{courier_id}", CourierView),
        web.get("/couriers/{courier_id}", CourierView),
        web.post("/orders", Orders),
        web.post("/orders/assign", OrdersAssign),
        web.post("/orders/complete", OrdersComplete),
    ]
)


def start_server() -> None:

    app.on_startup.append(connect_db)
    app.on_cleanup.append(disconnect_db)

    web.run_app(app)
