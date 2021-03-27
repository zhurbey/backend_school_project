from enum import Enum


class CouriersTypes(str, Enum):
    foot = "foot"
    bike = "bike"
    car = "car"


class CouriersCapacity(int, Enum):
    foot = 10
    bike = 15
    car = 50
