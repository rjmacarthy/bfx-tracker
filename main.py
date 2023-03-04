import argparse
import os
from bfx_track import BfxTracker;

def main(args):
    tracker = BfxTracker(os.environ.get("BFX_AUTH_TOKEN"), args.refetch)
    tracker.track(args.ccys)    
    for ccy in args.ccys:
        for wallet in args.wallets:
            if args.plot:
              tracker.plot(ccy, wallet)
            tracker.print_balance(ccy, wallet)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ccys', nargs='+', required=True,
                        help='List of ccys to fetch ledgers for')
    parser.add_argument('--wallets', nargs='+', required=True,
                        help='List of wallets to fetch balances for')
    parser.add_argument('--refetch', action='store_true',
                        help='If specified, re-fetches the ledgers from Bitfinex')
    parser.add_argument('--plot', action='store_true',
                        help='If specified, generates plots of the balances')
    parser.add_argument('--print', action='store_true',
                        help='If specified, prints the current balances to the console')
    parser.add_argument('--h', action='store_true',
                        help='Prints this help message and exits')
    args = parser.parse_args()
    if args.h:
        parser.print_help()
        exit(0)
    main(args)
    
