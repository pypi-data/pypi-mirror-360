import logging
import random
from datetime import datetime, timedelta

from faker import Faker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker()


def gps_factory(num_entries=120):
    base_time = datetime.utcnow()
    gps_data = []
    for i in range(num_entries):
        timestamp = (base_time + timedelta(seconds=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
        entry = {
            "time": timestamp,
            "latitude": round(fake.latitude(), 6),
            "longitude": round(fake.longitude(), 6),
            "accuracy": round(random.uniform(5.0, 50.0), 2),
            "altitude": round(random.uniform(100.0, 1000.0), 2),
            "speed": round(random.uniform(0.0, 120.0), 2),
            "bearing": f"{fake.word()}",
            "available": {
                "accuracy": random.choice([True, False]),
                "altitude": random.choice([True, False]),
                "bearing": random.choice([True, False]),
                "date": random.choice([True, False]),
                "latlon": random.choice([True, False]),
                "speed": random.choice([True, False]),
                "time": random.choice([True, False]),
            },
        }
        gps_data.append(entry)

    return {"data": gps_data}
