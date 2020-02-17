import pandas as pd


_DATERNG = pd.Timedelta(weeks=8)


schema = {
    "actions": {
        "size": 1000,
        "fields": {
            "userid": {"values": range(100)},
            "action": {"values": ["on", "off"]},
            "timestamp": {
                "values": pd.date_range(
                    pd.Timestamp.now() - _DATERNG,
                    periods=_DATERNG.total_seconds() // 60,
                    freq="min",
                ),
                "sort": True,
            },
        },
    },
    "employees": {
        "size": 100,
        "fields": {
            "id": {"values": range(10000)},
            "dept": {"values": range(5)},
            "hired": {
                "values": pd.date_range(
                    pd.Timestamp.now() - _DATERNG,
                    periods=_DATERNG.total_seconds() // (60 * 24),
                    freq="D",
                ),
                "sort": True,
            },
        },
    },
    "dept": {
        "size": 5,
        "fields": {
            "id": {"values": range(5), "repeat": False, "sort": True},
            "dname": {
                "values": ["sales", "it", "finance", "hr", "estates"],
                "repeat": False,
            },
        },
    },
}
