import logging
from datetime import datetime, timedelta

from faker import Faker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker()


def signal_factory():
    units = ["RPM", "km/h", "m/s", "kPa", "degC"]
    param_types = ["NUMBER", "STRING", "TEXT"]
    signal_types = ["SIGNAL", "DID", "PID", "DMR"]
    return [
        {
            "name": f"Signal_{fake.word()}_{fake.random_int(min=1000, max=9999)}",
            "unit": fake.random_element(units),
            "paramType": fake.random_element(param_types),
            "signalType": fake.random_element(signal_types),
            "paramId": f"param_{fake.random_int(min=1000, max=9999)}",
            "data": [
                {
                    "value": fake.pyfloat(
                        min_value=1000, max_value=10000000, right_digits=1
                    ),
                    "time": (
                        fake.date_time_between(start_date="-1d", end_date="now")
                        + timedelta(seconds=i)
                    ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
                for i in range(120)
            ],
        }
    ]
