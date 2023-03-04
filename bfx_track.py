from typing import List
import requests
import json
import pandas as pd
import os
import time
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d

METHOD: str = "getLedgers"
URL: str = "https://report.bitfinex.com/api/json-rpc"
LIMIT = 1000
WALLETS: List[str] = ["exchange", "margin", "funding", "contribution"]
DATE_FROM: str = "2013-04-01"
DEFAULT_HEADERS = {
    "bfx-nonce": str(int(time.time() * 1000)),
    "Content-Type": "application/json",
}


class BfxTracker:
    def __init__(self, auth_token, refetch=False):
        self.auth_token = auth_token
        self.create_folders()
        self.refetch = refetch

    def create_folders(self):
        if not os.path.exists("./data"):
            os.mkdir("data")
        if not os.path.exists("./data/raw"):
            os.mkdir("./data/raw")
        if not os.path.exists("./data/processed"):
            os.mkdir("./data/processed")

    def track(self, ccys: List[str]):
        for ccy in ccys:
            ccyp = self.get_ledgers(ccy)
            if os.path.exists(os.path.join("./data/raw", f"{ccy}.json")) and not self.refetch:
                print(
                    f"Skipping {ccy} as it has already been fetched, use refetch=True to refresh")
                continue

            self.fetch(ccyp, ccy)
            for wallet in WALLETS:
                self.process(ccy, wallet)

    def get_ledgers_request(self, ccy: str):
        return json.dumps({
            "auth": {
                "authToken": self.auth_token
            },
            "method": METHOD,
            "params": {
                "start": int(time.mktime(time.strptime(DATE_FROM, "%Y-%m-%d")) * 1000),
                "end": int(time.time() * 1000),
                "limit": LIMIT,
                "symbol": [ccy]
            }
        })

    def get_ledgers(self, ccy: str):
        return self.get_ledgers_request(ccy)

    def fetch(self, payload, ccy: str):
        headers = DEFAULT_HEADERS
        headers["bfx-token"] = self.auth_token
        r = requests.post(URL, headers=headers, data=payload)
        data = r.json()
        
        if not data["result"]:
            print(f"Skipping {ccy} as it has no data")
            return
        
        with open(os.path.join("./data/raw", f"{ccy}.json"), "w") as f:
            json.dump(data["result"]["res"], f)

    def plot(self, ccy: str, wallet: str = 'exchange'):
        if not os.path.exists(f"./data/processed/{ccy}/{wallet}.csv"):
            print (f"Skipping plot of {ccy} for {wallet} as it has no data")
            return
        
        df = pd.read_csv(f"./data/processed/{ccy}/{wallet}.csv")
        _, ax = plt.subplots(figsize=(10, 6))
        y_smooth = gaussian_filter1d(df["balance"], sigma=2)
        ax.plot(df["date"], y_smooth, marker="o", markersize=2)
        ax.set_xlabel("Date")
        ax.set_ylabel(f"Balance {ccy}")
        ax.set_title(f"Bitfinex Daily Balance {wallet} {ccy}")
        plt.show()

    def print_balance(self, ccy: str, wallet: str):
        if not os.path.exists(f"./data/processed/{ccy}/{wallet}.csv"):
            return
        df = pd.read_csv(f"./data/processed/{ccy}/{wallet}.csv")
        print(f"{ccy} {wallet}: {df.iloc[0]['balance']}")
        return df.iloc[0]["balance"]

    def save_processed(self, df, wallet: str, ccy: str):
        if not os.path.exists(f"./data/processed/{ccy}"):
            os.mkdir(os.path.join(f"./data/processed", ccy))
        save_path = os.path.join(
            f"./data/processed/{ccy}", f"{wallet}.csv")
        df.to_csv(save_path, index=False)

    def get_processed(self, ccy: str, wallet: str):
        if os.path.exists(f"./data/processed/{ccy}/{wallet}.csv"):
            return pd.read_csv(f"./data/processed/{ccy}/{wallet}.csv").to_json(orient="records")

    def process(self, ccy: str, wallet: str):
        df = pd.read_json(f"./data/raw/{ccy}.json")
        df = df[df["wallet"] == wallet]
        if df.empty:
            return
        df["mts"] = df["mts"].apply(lambda x: pd.to_datetime(x, unit="ms"))
        df["emptyFill"] = df["amount"].apply(lambda x: 1 if x == 0 else 0)
        df.set_index("mts", inplace=True)
        df_balances = df["balance"].resample("D").last()
        df_daily = pd.DataFrame(df_balances)
        df_daily = df_daily.reset_index().rename(columns={
            "mts": "date"})
        df_daily["balance"].fillna(method="ffill", inplace=True)
        df_daily.sort_values(
            by="date", inplace=True, ascending=False)
        self.save_processed(df_daily, wallet, ccy)
