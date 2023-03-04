# Bitfinex Balance Tracker

This script allows you to fetch balances and ledgers from Bitfinex for a specified list of cryptocurrencies (ccys) and wallets. It provides additional options for re-fetching the ledgers, generating plots of the balances, and printing the current balances to the console.

## Prerequisites

- Python 3.x
- Bitfinex Token

## Installation

1. Clone the repository.
2. Install the required packages: `pip install -r requirements.txt`
3. Rename `.env.example` to `.env` and update the `BFX_AUTH_TOKEN`

## Usage

Here's a breakdown of the available arguments:

- `--ccys`: A list of cryptocurrencies (ccys) to fetch ledgers for. This is a required argument and should be specified as follows: `--ccys BTC ETH XRP`.
- `--wallets`: A list of wallets to fetch balances for. This is a required argument and should be specified as follows: `--wallets margin exchange funding contribution`.
- `--refetch`: If specified, re-fetches the ledgers from Bitfinex. This is an optional argument and should be used as follows: `--refetch`.
- `--plot`: If specified, generates plots of the balances. This is an optional argument and should be used as follows: `--plot`.
- `--print`: If specified, prints the current balances to the console. This is an optional argument and should be used as follows: `--print`.
- `--h`: Prints the help message and exits. This is an optional argument and should be used as follows: `--h`.

### Examples

```
python main.py --ccys BTC ETH --wallets margin funding
python main.py --ccys BTC ETH --refetch --plot
python main.py --ccys BTC ETH XRP --wallets exchange
```