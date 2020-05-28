import numpy as np
import pandas as pd
from faker import Faker


nweeks = 80
_DATERNG = pd.Timedelta(weeks=nweeks)

fake = Faker("en_GB")


schema = {
    "employees": {
        "size": 200,
        "fields": {
            "employee_id": {"values": range(100, 500), "repeat": False},
            "first_name": {"values": [fake.first_name() for _ in range(400)]},
            "last_name": {"values": [fake.last_name() for _ in range(400)]},
            "phone_number": {"values": [fake.phone_number() for _ in range(400)]},
            "email": {"values": [fake.safe_email() for _ in range(400)]},
            "hire_date": {"values": []},
            "hire_date": {
                "values": pd.date_range(
                    pd.Timestamp.now().date() - (_DATERNG),
                    periods=nweeks * 7 * 2,
                    freq="D",
                ),
                "sort": True,
            },
            "job_id": {"values": range(1000, 2000), "repeat": False},
            "salary": {"values": range(20000, 100000)},
            "manager_id": {"values": range(100, 150)},
            "department_id": {"values": range(10, 40)},
        },
    },
    "departments": {
        "size": 30,
        "fields": {
            "department_id": {"values": range(10, 40), "repeat": False},
            "department_name": {"values": [fake.bs() for _ in range(30)]},
        },
    },
    "customers": {
        "size": 1000,
        "fields": {
            "customer_id": {"values": range(5000, 6000), "repeat": False},
            "first_name": {"values": [fake.first_name() for _ in range(1000)]},
            "last_name": {"values": [fake.last_name() for _ in range(1000)]},
            "phone": {"values": [fake.msisdn() for _ in range(1000)], "repeat": False},
            "email": {
                "values": [fake.safe_email() for _ in range(1000)],
                "repeat": False,
            },
            "street": {
                "values": [
                    fake.street_address().replace("\n", ", ") for _ in range(1000)
                ],
                "repeat": False,
            },
            "city": {"values": [fake.city() for _ in range(1000)]},
            "postal_code": {"values": [fake.postcode() for _ in range(1000)]},
        },
    },
    "orders": {
        "size": 5000,
        "fields": {
            "order_no": {"values": range(5000), "repeat": False, "sort": True},
            "order_time": {
                "values": pd.date_range(
                    pd.Timestamp.now() - (_DATERNG),
                    periods=nweeks * 7 * 2 * 24,
                    freq="H",
                ),
                "sort": True,
            },
            "customer_id": {"values": range(5000, 6000)},
            "salesperson_id": {"values": range(100, 500)},
            "category_id": {"values": range(1, 11)},
            "value": {
                "values": np.around(
                    np.random.lognormal(
                        mean=np.log(5), sigma=np.log(5), size=1000
                    ).clip(1),
                    2,
                )
            },
        },
    },
}
