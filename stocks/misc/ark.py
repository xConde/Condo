import json

import pandas as pd
import requests
import random
from bs4 import BeautifulSoup

user_agent_strings = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:86.1) Gecko/20100101 Firefox/86.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:86.1) Gecko/20100101 Firefox/86.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:82.1) Gecko/20100101 Firefox/82.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:86.0) Gecko/20100101 Firefox/86.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:86.0) Gecko/20100101 Firefox/86.0",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:83.0) Gecko/20100101 Firefox/83.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:84.0) Gecko/20100101 Firefox/84.0",
]


def get_ark_daily():
    url_orders = "https://cathiesark.com/ark-funds-combined/trades"

    raw_page = requests.get(url_orders, headers={"User-Agent": random.choice(user_agent_strings)}).text

    parsed_script = BeautifulSoup(raw_page, features='lxml').find(
        "script", {"id": "__NEXT_DATA__"}
    )

    parsed_json = json.loads(parsed_script.string)

    df_orders = pd.json_normalize(parsed_json["props"]["pageProps"]["arkTrades"])
    df_orders.drop(
        [
            "everything",
            "everything.profile.customThumbnail",
            "hidden",
            "images.thumbnail",
        ],
        axis=1,
        inplace=True,
    )

    df_orders["date"] = pd.to_datetime(df_orders["date"], format="%Y-%m-%dZ").dt.date

    return df_orders.loc[0:20].to_string(index=False)

def get_ark_holdings():
    url_orders = "https://cathiesark.com/ark-funds-combined/complete-holdings"

    raw_page = requests.get(url_orders, headers={"User-Agent": random.choice(user_agent_strings)}).text

    parsed_script = BeautifulSoup(raw_page, features='lxml').find(
        "script", {"id": "__NEXT_DATA__"}
    )

    parsed_json = json.loads(parsed_script.string)

    df_orders = pd.json_normalize(parsed_json["props"]["pageProps"]["arkPositions"])
    df_orders.drop(
        [
            # "everything",
            # "everything.profile.customThumbnail",
            # "hidden",
            "images.thumbnail",
        ],
        axis=1,
        inplace=True,
    )
    #
    # df_orders["date"] = pd.to_datetime(df_orders["date"], format="%Y-%m-%dZ").dt.date
    #

    print(df_orders.loc[0:20].to_string(index=False))
    return df_orders.loc[0:20].to_string(index=False)
