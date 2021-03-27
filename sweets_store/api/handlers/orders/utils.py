import typing as t

from asyncpg import Record  # type: ignore

from sweets_store.api.handlers.couriers.constants import CouriersCapacity
from sweets_store.utils.dates import do_time_intervals_intersect


def filter_orders_for_courier(courier: Record, orders: t.List[Record]) -> t.List[Record]:
    capacity = CouriersCapacity[courier["courier_type"]]
    regions, working_hours = courier["regions"], courier["working_hours"]

    filtered_orders = []
    for order_ in orders:

        if order_["weight"] > capacity:
            continue

        if order_["region"] not in regions:
            continue

        # Check if delivery hours for order and working hours for courier intersect
        if not do_time_intervals_intersect(working_hours, order_["delivery_hours"]):
            continue

        filtered_orders.append(order_)

    return filtered_orders


def get_best_orders_subset(courier: Record, orders: t.List[Record]) -> t.List[Record]:
    capacity = CouriersCapacity[courier["courier_type"]]
    sorted_orders = sorted(orders, key=lambda order: t.cast(float, order["weight"]))

    bundle_weight = 0
    best_orders = []

    for order in sorted_orders:
        if bundle_weight + order["weight"] > capacity:
            break

        bundle_weight += order["weight"]
        best_orders.append(order)

    return best_orders
