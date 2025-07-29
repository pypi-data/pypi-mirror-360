
import argparse
import logging
import sys
import json

from .common import val_arg, val_run
from .api import CoinSpotApi

logger = logging.getLogger(__name__)

debug = False

def process_get(args):
    """
    Handle get type requests for the public api
    """

    # Process incoming arguments
    val_arg(isinstance(args.url, str), "Invalid type for URL")
    val_arg(args.url != "", "Empty URL provided")

    # Api for coinspot access
    api = CoinSpotApi()

    # Make request against the API
    response = api.get(args.url, raw_output=args.raw_output)

    # Display output from the API, formatting if required
    print_output(args, response)

def process_post(args):
    """
    Process post type requests for the private and read-only api
    """

    # Process incoming arguments
    val_arg(isinstance(args.url, str), "Invalid type for URL")
    val_arg(args.url != "", "Empty URL provided")

    # Api for coinspot access
    api = CoinSpotApi()

    # Read payload from stdin
    payload = sys.stdin.read()

    # Make request against the API
    response = api.post(args.url, payload, raw_payload=args.raw_input, raw_output=args.raw_output)

    # Display output from the API, formatting if required
    print_output(args, response)

def process_balance(args):
    """
    Process request to display balances for the account
    """

    # Api for coinspot access
    api = CoinSpotApi()

    url = "/api/v2/ro/my/balances"

    if args.cointype is not None:
        val_arg(isinstance(args.cointype, str), "Invalid cointype supplied")
        val_arg(args.cointype != "", "Empty coin type provided")

        url = f"/api/v2/ro/my/balance/{args.cointype}?available=yes"

    # Request balance info
    response = api.post(url, "{}", raw_output=args.raw_output)

    print_output(args, response)

def process_price_history(args):
    """
    Process request to display price history for a coin type
    """

    # Validate incoming arguments
    val_arg(isinstance(args.cointype, str) and args.cointype != "", "Invalid cointype supplied")
    val_arg(isinstance(args.reference_price, (float, int, type(None))), "Invalid reference price supplied")
    val_arg(args.age != "", "Invalid age supplied")

    # Parse age
    age = args.age
    mod = 1

    if age.endswith("h"):
        age = age[:-1]
    elif age.endswith("d"):
        age = age[:-1]
        mod = 24
    elif age.endswith("w"):
        age = age[:-1]
        mod = 24 * 7

    val_arg(age.isdigit(), f"Age is not a valid format: {age}")
    age = int(age) * mod

    # Api for coinspot access
    api = CoinSpotApi()

    # Request balance info
    response = api.get_price_history(args.cointype, age_hours=age, stats=args.stats, reference_price=args.reference_price)

    print_output(args, response)

def process_order_history(args):
    """
    Process request to display order history for the account
    """

    # Api for coinspot access
    api = CoinSpotApi()

    url = "/api/v2/ro/my/orders/completed"

    request = {
        "limit": 200
    }

    # Limit to coin type, if requested
    if args.cointype is not None:
        val_arg(isinstance(args.cointype, str), "Invalid type for cointype")

        request["cointype"] = args.cointype

    # Adjust limit
    if args.limit is not None:
        val_arg(isinstance(args.limit, int), "Invalid type for limit")
        # Don't validate the limit range - Let the api endpoint do this

        request["limit"] = args.limit

    # Start date
    if args.start_date is not None:
        val_arg(isinstance(args.start_date, str), "Invalid type for start date")

        request["startdate"] = args.start_date

    # End date
    if args.end_date is not None:
        val_arg(isinstance(args.end_date, str), "Invalid type for end date")

        request["enddate"] = args.end_date

    # Request order history
    response = api.post(url, request, raw_output=args.raw_output)

    print_output(args, response)

def process_market_buy(args):
    """
    Place market buy order
    """

    # Validate incoming parameters
    val_arg(isinstance(args.rate, (float, type(None))), "Invalid type for rate")
    val_arg(isinstance(args.amount, float), "Invalid type for amount")

    # Coinspot api
    api = CoinSpotApi()

    url = "/api/v2/my/buy"

    # Determine the rate - If there is no rate supplied, then use the asking
    # price from the API to determine the buy price
    rate = args.rate
    if rate is None:
        prices = json.loads(api.get(f"/pubapi/v2/latest/{args.cointype}"))
        logger.info("Current prices: %s", prices["prices"])
        rate = prices["prices"]["ask"]

    rate = float(rate)

    amount = args.amount
    if args.amount_type == "aud":
        amount = amount/rate
        logger.info("Calculated coin quantity: %s", amount)

    logger.info("Effective aud amount: %s", round(amount, 8) * rate)

    request = {
        "cointype": args.cointype,
        "amount": amount,
        "rate": rate
    }

    # Lodge the buy request
    response = api.post(url, request, raw_output=args.raw_output)

    print_output(args, response)

def process_market_sell(args):
    """
    Place market sell order
    """

    # Validate incoming parameters
    val_arg(isinstance(args.rate, (float, type(None))), "Invalid type for rate")
    val_arg(isinstance(args.amount, float), "Invalid type for amount")

    # Coinspot api
    api = CoinSpotApi()

    url = "/api/v2/my/sell"

    # Determine the rate - If there is no rate supplied, then use the bidding
    # price from the API to determine the sell price
    rate = args.rate
    if rate is None:
        prices = json.loads(api.get(f"/pubapi/v2/latest/{args.cointype}"))
        logger.info("Current prices: %s", prices["prices"])
        rate = prices["prices"]["bid"]

    rate = float(rate)

    amount = args.amount
    if args.amount_type == "aud":
        amount = amount/rate
        logger.info("Calculated coin quantity: %s", amount)

    amount = round(amount, 8)
    logger.info("Effective aud amount: %s", amount * rate)

    request = {
        "cointype": args.cointype,
        "amount": amount,
        "rate": rate
    }

    # Lodge the sell request
    response = api.post(url, request, raw_output=args.raw_output)

    print_output(args, response)

def process_market_orders(args):
    """
    Display open market orders
    """

    # Coinspot api
    api = CoinSpotApi()

    url = "/api/v2/ro/my/orders/market/open"
    if args.completed:
        url = "/api/v2/ro/my/orders/market/completed"

    request = {
        "limit": 200
    }

    # Limit to coin type, if requested
    if args.cointype is not None:
        val_arg(isinstance(args.cointype, str), "Invalid type for cointype")
        val_arg(args.cointype != "", "Invalid value for cointype")

        request["cointype"] = args.cointype

    # Adjust limit
    if args.limit is not None:
        val_arg(isinstance(args.limit, int), "Invalid type for limit")
        # Don't validate the limit range - Let the api endpoint do this

        request["limit"] = args.limit

    # Start date
    if args.start_date is not None:
        val_arg(isinstance(args.start_date, str), "Invalid type for start date")

        request["startdate"] = args.start_date

    # End date
    if args.end_date is not None:
        val_arg(isinstance(args.end_date, str), "Invalid type for end date")

        request["enddate"] = args.end_date

    # Request market orders
    response = api.post(url, request, raw_output=args.raw_output)

    print_output(args, response)

def process_simple_buy_sell(args):
    """
    Process simple buy sell
    """

    # Validate incoming parameters
    val_arg(args.cointype != "", "Invalid cointype supplied")
    val_arg(args.age != "", "Invalid age supplied")
    val_arg(isinstance(args.amount, float), "Invalid amount supplied")
    val_arg(args.amount > 0, "Invalid amount supplied")
    val_arg(isinstance(args.buy_pct, float), "Invalid buy pct supplied")
    val_arg(isinstance(args.sell_pct, float), "Invalid sell pct supplied")
    val_arg(isinstance(args.limit, int), "Invalid limit supplied")
    val_arg(args.limit > 0, "Invalid limit supplied")

    # Coinspot api
    api = CoinSpotApi()

    # Parse age
    age = args.age
    mod = 1

    if age.endswith("h"):
        age = age[:-1]
    elif age.endswith("d"):
        age = age[:-1]
        mod = 24
    elif age.endswith("w"):
        age = age[:-1]
        mod = 24 * 7

    val_arg(age.isdigit(), f"Age is not a valid format: {age}")
    age = int(age) * mod
    logger.info("Price history for last %s hours", age)

    # Coin should be uppercase
    coin = args.cointype.upper()

    # Retrieve amount available from balance
    response = json.loads(api.post("/api/v2/ro/my/balance/aud?available=yes", {}))
    val_run("balance" in response, "Missing balance key in coinspot API response")
    val_run("AUD" in response["balance"], "Missing AUD key in coinspot API response")
    val_run("available" in response["balance"]["AUD"], "Missing available amount in coinspot API response")
    aud_available = float(response["balance"]["AUD"]["available"])

    logger.info("AUD available: %s", aud_available)

    # Stop here if the balance can't meet the purchase amount
    if aud_available < args.amount:
        logger.info(f"Available balance can't meet the purchase amount: {args.amount}")
        return

    # Retrieve the current coin prices
    response = json.loads(api.get(f"/pubapi/v2/latest/{coin}"))
    val_run("prices" in response, "API response missing 'prices' key")
    val_run("bid" in response["prices"], "API response missing 'bid' key")
    val_run("ask" in response["prices"], "API response missing 'ask' key")

    bid_price = float(response["prices"]["bid"])
    ask_price = float(response["prices"]["ask"])

    logger.info("Coin prices: %s ask, %s bid", ask_price, bid_price)

    # Retrieve coin pricing statistics
    stats = json.loads(api.get_price_history(coin, age_hours=age, stats=True, reference_price=ask_price))

    # If the current price is x pct lower than average, then buy, otherwise,
    # we stop here
    avg_price_diff = stats["reference"]["avg_price_diff_pct"]
    if avg_price_diff < args.buy_pct:
        logger.info("Buy criteria not met. Buy Pct: %s. Avg Price Diff: %s", args.buy_pct, avg_price_diff)
        return

    # Buy the coin at bid price
    coin_amount = args.amount / ask_price
    request = {
        "cointype": coin,
        "amount": coin_amount,
        "rate": ask_price
    }

    logger.debug("Buy Order Request: %s", json.dumps(request))
    response = api.post("/api/v2/my/buy", request)
    logger.debug("Buy Order Response: %s", response)
    buy_response = json.loads(response)

    # Wait until the order is no longer an open order (i.e. purchased)
    # TODO

    # Create a sell order for the amount x the sell pct
    sell_rate = ask_price * (args.sell_pct/100 + 1)
    request = {
        "cointype": coin,
        "amount": coin_amount,
        "rate": sell_rate
    }

    logger.debug("Sell Order Request: %s", json.dumps(request))
    response = api.post("/api/v2/my/sell", request)
    logger.debug("Sell Order Response: %s", response)
    sell_response = json.loads(response)

    # Display summary information
    buy_amount_aud = buy_response["amount"] * buy_response["rate"]
    sell_amount_aud = sell_response["amount"] * sell_response["rate"]

    print_output(args, json.dumps({
        "buy": {
            "id": buy_response["id"],
            "rate": buy_response["rate"],
            "amount": buy_response["amount"],
            "amount_aud": buy_amount_aud
        },
        "sell": {
            "id": sell_response["id"],
            "rate": sell_response["rate"],
            "amount": sell_response["amount"],
            "amount_aud": sell_amount_aud
        },
        "profit_on_sale": sell_amount_aud - buy_amount_aud
    }))

def add_common_args(parser):
    """
    Common arguments for all subcommands
    """

    # Process incoming arguments
    val_arg(isinstance(parser, argparse.ArgumentParser), "Invalid parser supplied to add_common_args")

    # Debug option
    parser.add_argument(
        "-d", action="store_true", dest="debug", help="Enable debug output"
    )

    # Json formatting options
    parser.add_argument("--raw-output", action="store_true", dest="raw_output", help="Raw (unpretty) json output")

def print_output(args, output):
    """
    Display the response output, with option to display raw or pretty formatted
    """

    # Process incoming arguments
    val_arg(isinstance(args.raw_output, bool), "Invalid type for raw_output")
    val_arg(isinstance(output, str), "Invalid output supplied to print_output")

    # Display output raw or pretty
    if args.raw_output:
        print(output)
    else:
        print(json.dumps(json.loads(output), indent=4))

def process_args():
    """
    Processes csutl command line arguments
    """

    # Create parser for command line arguments
    parser = argparse.ArgumentParser(
        prog="csutl", description="CoinSpot Utility", exit_on_error=False
    )

    parser.set_defaults(debug=False)

    # Parser configuration
    #parser.add_argument(
    #    "-d", action="store_true", dest="debug", help="Enable debug output"
    #)

    parser.set_defaults(call_func=None)
    subparsers = parser.add_subparsers(dest="subcommand")

    # post subcommand
    subcommand_post = subparsers.add_parser(
        "post",
        help="Perform a post request against the CoinSpot API"
    )
    subcommand_post.set_defaults(call_func=process_post)
    add_common_args(subcommand_post)

    subcommand_post.add_argument("url", help="URL endpoint")
    subcommand_post.add_argument("--raw-input", action="store_true", dest="raw_input", help="Don't parse input or add nonce")

    # get subcommand
    subcommand_get = subparsers.add_parser(
        "get",
        help="Perform a get request against the CoinSpot API"
    )
    subcommand_get.set_defaults(call_func=process_get)
    add_common_args(subcommand_get)

    subcommand_get.add_argument("url", help="URL endpoint")

    # Balance
    subcommand_balance = subparsers.add_parser(
        "balance",
        help="Retrieve account balance"
    )
    subcommand_balance.set_defaults(call_func=process_balance)
    add_common_args(subcommand_balance)

    subcommand_balance.add_argument("-t", action="store", dest="cointype", help="Coin type", default=None)

    # Price history
    subcommand_price_history = subparsers.add_parser(
        "price_history",
        help="Retrieve price history"
    )
    subcommand_price_history.set_defaults(call_func=process_price_history)
    add_common_args(subcommand_price_history)

    subcommand_price_history.add_argument("-s", action="store_true", dest="stats", help="Display stats")
    subcommand_price_history.add_argument("-a", action="store", dest="age", help="Age (e.g. 4h or 3d) (default 1d)", default="1d")
    subcommand_price_history.add_argument("-r", action="store", dest="reference_price", type=float, help="Reference price", default=None)
    subcommand_price_history.add_argument("cointype", action="store", help="Coin type")

    # order history
    subcommand_order_history = subparsers.add_parser(
        "order_history",
        help="Retrieve account order history"
    )
    subcommand_order_history.set_defaults(call_func=process_order_history)
    add_common_args(subcommand_order_history)

    subcommand_order_history.add_argument("-s", action="store", dest="start_date", help="Start date", default=None)
    subcommand_order_history.add_argument("-e", action="store", dest="end_date", help="End date", default=None)
    subcommand_order_history.add_argument("-l", action="store", dest="limit", help="Result limit (default 200, max 500)", type=int, default=None)
    subcommand_order_history.add_argument("-t", action="store", dest="cointype", help="coin type", default=None)

    # simple buy sell
    subcommand_simple_buy_sell = subparsers.add_parser(
        "simple_buy_sell",
        help="Simple buy sell"
    )
    subcommand_simple_buy_sell.set_defaults(call_func=process_simple_buy_sell)
    add_common_args(subcommand_simple_buy_sell)

    subcommand_simple_buy_sell.add_argument("cointype", action="store", help="Coin type")
    subcommand_simple_buy_sell.add_argument("amount", action="store", help="Amount to buy (aud)", type=float)
    subcommand_simple_buy_sell.add_argument("-a", action="store", dest="age", help="Age for price history (e.g. 4h or 3d) (default 1d)", default="1d")
    subcommand_simple_buy_sell.add_argument("-b", action="store", dest="buy_pct", help="Pct drop to allow buy (e.g. 2 is a 2 pct drop)", type=float, default=3)
    subcommand_simple_buy_sell.add_argument("-s", action="store", dest="sell_pct", help="Pct profit to sell for (e.g. 5 is 5 pct increase)", type=float, default=2)
    subcommand_simple_buy_sell.add_argument("-l", action="store", dest="limit", help="Limit on open orders (default 50)", type=int, default=50)


    # market orders
    subcommand_market = subparsers.add_parser(
        "market",
        help="Market orders"
    )
    subparsers_market = subcommand_market.add_subparsers(dest="market_subcommand")

    # Market orders
    subcommand_market_orders = subparsers_market.add_parser(
        "orders",
        help="Market orders"
    )
    subcommand_market_orders.set_defaults(call_func=process_market_orders)
    add_common_args(subcommand_market_orders)

    subcommand_market_orders.add_argument("-s", action="store", dest="start_date", help="Start date", default=None)
    subcommand_market_orders.add_argument("-e", action="store", dest="end_date", help="End date", default=None)
    subcommand_market_orders.add_argument("-l", action="store", dest="limit", help="Result limit (default 200, max 500)", type=int, default=None)
    subcommand_market_orders.add_argument("-t", action="store", dest="cointype", help="coin type", default=None)
    subcommand_market_orders.add_argument("-c", action="store_true", dest="completed", help="Show completed orders")

    # Market buy order
    subcommand_market_buy = subparsers_market.add_parser(
        "buy",
        help="Place buy order"
    )
    subcommand_market_buy.set_defaults(call_func=process_market_buy)
    add_common_args(subcommand_market_buy)

    subcommand_market_buy.add_argument("cointype", action="store", help="coin type")
    subcommand_market_buy.add_argument("amount_type", action="store", help="Amount type", choices=("aud", "coin"))
    subcommand_market_buy.add_argument("amount", action="store", help="Amount", type=float)
    subcommand_market_buy.add_argument("-r", action="store", dest="rate", help="rate", default=None, type=float)

    # Market sell order
    subcommand_market_sell = subparsers_market.add_parser(
        "sell",
        help="Place sell order"
    )
    subcommand_market_sell.set_defaults(call_func=process_market_sell)
    add_common_args(subcommand_market_sell)

    subcommand_market_sell.add_argument("cointype", action="store", help="coin type")
    subcommand_market_sell.add_argument("amount_type", action="store", help="Amount type", choices=("aud", "coin"))
    subcommand_market_sell.add_argument("amount", action="store", help="Amount", type=float)
    subcommand_market_sell.add_argument("-r", action="store", dest="rate", help="rate", default=None, type=float)

    # Parse arguments
    args = parser.parse_args()

    # Capture argument options
    global debug
    debug = args.debug

    # Logging configuration
    level = logging.INFO
    if debug:
        level = logging.DEBUG

    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    # Run the sub command
    if args.call_func is None:
        logger.error("Missing subcommand")
        parser.print_help()
        return 1

    return args.call_func(args)

def main():
    ret = 0

    try:
        process_args()

    except BrokenPipeError as e:
        try:
            print("Broken Pipe", file=sys.stderr)
            if not sys.stderr.closed:
                sys.stderr.close()
        except:
            pass

        ret = 1

    except Exception as e: # pylint: disable=board-exception-caught
        if debug:
            logger.error(e, exc_info=True, stack_info=True)
        else:
            logger.error(e)

        ret = 1

    try:
        sys.stdout.flush()
    except Exception as e:
        ret = 1

    sys.exit(ret)

