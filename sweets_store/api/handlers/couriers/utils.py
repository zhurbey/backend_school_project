import typing as t
from datetime import datetime
from statistics import mean

from asyncpg import Record  # type: ignore

from sweets_store.utils.dates import datetime_delta_to_seconds

from .constants import EarningsCoefficient


def calculate_courier_rating(t_constant: float) -> float:

    return ((3600 - min(t_constant, 3600)) / 3600) * 5


def calculate_courier_earnings(finished_bundles: t.List[Record]) -> int:
    result = 0

    for bundle in finished_bundles:
        coefficient = EarningsCoefficient[bundle["courier_type"]]
        result += 500 * coefficient

    return result


def get_best_region_average_time(bundles_aggregations: t.List[Record]) -> float:

    # region_number -> List[orders completion time lengths(datetime interval and then seconds)]
    regions_times: t.Dict[int, t.List[t.Any]] = {}

    for bundle_row in bundles_aggregations:
        orders = []

        for complete_time, region in zip(bundle_row["complete_times"], bundle_row["regions"]):
            orders.append((complete_time, region))

        orders.sort(key=lambda order_: t.cast(datetime, order_[0]))  # sort by complete times
        for i, order_ in enumerate(orders):
            if i == 0:
                completion_time_delta = order_[0] - bundle_row["assign_time"]
            else:
                completion_time_delta = order_[0] - orders[i - 1][0]

            region_completion_times = regions_times.get(order_[1], [])
            region_completion_times.append(completion_time_delta)
            regions_times[order_[1]] = region_completion_times

    for key, value in regions_times.items():
        # Convert complete times from datetime deltas to seconds
        complete_times = list(map(datetime_delta_to_seconds, value))
        regions_times[key] = complete_times

    average_regions_times = list(map(mean, regions_times.values()))
    return t.cast(float, min(average_regions_times))
