import numpy as np
import pandas as pd
from pycountry import countries


nweeks = 80
_DATERNG = pd.Timedelta(weeks=nweeks)


schema = {
    "device": {
        "size": nweeks * 7 * 2,
        "fields": {
            "date": {
                "values": pd.date_range(
                    # Ensure send dates are always before receive dates
                    pd.Timestamp.now().date() - (_DATERNG * 2),
                    periods=nweeks * 7 * 2,
                    freq="D",
                ),
                "sort": True,
            },
            "platform": {"values": ["Android", "iOS"], "priors": [0.5, 0.5]},
            "num_users": {"values": range(1000000)},
            "country": {
                "values": np.random.choice([cc.alpha_2 for cc in countries], 10)
            },
        },
    }
}
