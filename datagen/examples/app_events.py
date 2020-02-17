import pandas as pd


_DATERNG = pd.Timedelta(weeks=8)


schema = {
    "apps": {
        "size": 1000,
        "fields": {
            "appID": {"values": range(10)},
            "eventID": {"values": ["click", "impression"]},
            "timestamp": {
                "values": pd.date_range(
                    pd.Timestamp.now() - _DATERNG,
                    periods=round(_DATERNG.total_seconds()),
                    freq="s",
                ),
                "sort": True,
            },
        },
    },
}
