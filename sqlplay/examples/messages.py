import pandas as pd


_DATERNG = pd.Timedelta(weeks=8)


# Tables of sent and received messages.
# Question: Write a SQL statement to find the success rate for message transmission.
# Answer: Given that the expected fraction of message IDs in the data is ~0.8
# expect the answer to be around 0.8**2 == 0.64

nmsg = 100
ratio = 0.8

schema = {
    "sent": {
        "size": int(round(ratio, nmsg)),
        "fields": {
            "msgid": {"values": range(nmsg)},
            "timestamp": {
                "values": pd.date_range(
                    # Ensure send dates are always before receive dates
                    pd.Timestamp.now() - (_DATERNG) * 2,
                    periods=_DATERNG.total_seconds() // 60,
                    freq="min",
                ),
                "sort": True,
            },
        },
    },
    "received": {
        "size": int(round(ratio, nmsg)),
        "fields": {
            "msgid": {"values": range(nmsg)},
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
}
