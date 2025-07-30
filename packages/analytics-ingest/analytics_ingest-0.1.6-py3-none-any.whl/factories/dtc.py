# from datetime import datetime, timedelta
# from faker import Faker
# import random

# fake = Faker()

# def dtc_factory(num_entries=10):
#     base_time = datetime.utcnow()
#     dtc_data = []

#     for i in range(num_entries):
#         entry = {
#             "description": fake.sentence(nb_words=6),
#             "dtcId": f"DTC{random.randint(1000, 9999)}",
#             "extended": {
#                 "bytes": fake.hexify(text="^" * 8)  # 8-character hex string
#             } if random.choice([True, False]) else None,
#             "snapshot": {
#                 "bytes": fake.hexify(text="^" * 8)
#             } if random.choice([True, False]) else None,
#             "status": random.choice(["active", "inactive", "pending"]),
#             "time": (base_time + timedelta(seconds=i)).isoformat() + "Z",
#         }
#         dtc_data.append(entry)

import random

#     return {"data": dtc_data}
from datetime import datetime, timedelta

from faker import Faker

fake = Faker()

def dtc_factory(num_entries=10):
    base_time = datetime.utcnow()
    dtc_data = []

    for i in range(num_entries):
        entry = {
            "description": fake.sentence(nb_words=6),
            "dtcId": f"DTC{random.randint(1000, 9999)}",
            "extended": {
                "bytes": fake.hexify(text="^" * 8)  # 8-character hex string
            } if random.choice([True, False]) else None,
            "snapshot": {
                "bytes": fake.hexify(text="^" * 8)
            } if random.choice([True, False]) else None,
            "status": f"{random.randint(0, 255):02X}",
            # "statusBit": f"{random.randint(0, 255):02X}",  # <-- Ensure 2-digit hex
            "time": (base_time + timedelta(seconds=i)).isoformat() + "Z",
        }
        dtc_data.append(entry)

    return {"data": dtc_data}
