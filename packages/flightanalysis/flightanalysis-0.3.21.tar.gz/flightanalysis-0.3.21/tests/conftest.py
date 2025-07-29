from pytest import fixture
from flightdata import Flight, Origin


@fixture(scope="session")
def flight():
    return Flight.from_json('tests/data/p23_flight.json')


@fixture(scope="session")
def box():
    return Origin.from_f3a_zone('tests/data/p23_box.f3a')


