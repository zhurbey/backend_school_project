from enum import Enum


class CouriersTypes(str, Enum):
    foot = "foot"
    bike = "bike"
    car = "car"


class CouriersCapacity(int, Enum):
    foot = 10
    bike = 15
    car = 50


class EarningsCoefficient(int, Enum):
    foot = 2
    bike = 5
    car = 9
