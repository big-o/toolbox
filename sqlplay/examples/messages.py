import pandas as pd


_DATERNG = pd.Timedelta(weeks=8)


# Tables of sent and received messages.

# Question: What is the message delivery success rate per day?

nmsg = 100
ratio = 0.5

schema = {
    "sent": {
        "size": round(ratio * nmsg),
        "fields": {
            "msgid": {"values": range(nmsg), "repeat": False},
            "timestamp": {
                "values": pd.date_range(
                    # Ensure send dates are always before receive dates
                    pd.Timestamp.now() - (_DATERNG * 2),
                    periods=_DATERNG.total_seconds() // 60,
                    freq="min",
                ),
                "sort": True,
                "repeat": False,
            },
        },
    },
    "received": {
        "size": round(ratio * nmsg),
        "fields": {
            "msgid": {"values": range(nmsg), "repeat": False},
            "timestamp": {
                "values": pd.date_range(
                    pd.Timestamp.now() - _DATERNG,
                    periods=_DATERNG.total_seconds() // 60,
                    freq="min",
                ),
                "sort": True,
                "repeat": False,
            },
        },
    },
}
