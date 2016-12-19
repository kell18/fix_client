import sys
from fix_client import FixClient, Tags

TARGET_CASH_QUANTITY = 100000.0     # upper bound for total stocks cash quantity
STOCK_EXTRA = 50.0                  # extra per each market stock price
DEFAULT_LKOH_STOCK_PRICE = 3200.0   # in case of market price is not accepted

def main():
    if len(sys.argv) != 3:
        sys.exit("Error: need to pass adapter port and order ID (ClOrdID) as arguments.")
    port = int(sys.argv[1])
    order_id = sys.argv[2]

    with FixClient(('localhost', port), ["49=TEST", "56=QUIK"]) as client:
        resp, is_success = client.request_logon()
        if is_success:
            print("Logon successful.")
        else:
            sys.exit("Logon failed with response: `{0}`".format(resp))

        market_data = client.request(["35=V", "262=3", "263=1", "264=1", "265=0", "267=1",
                                      "269=1", "22=8", "48=LKOH", "100=MOEX"])
        if market_data[Tags.MsgType] == "W":
            print("MarketDataRequest successful.")
        else:
            sys.exit("MarketDataRequest failed: `{0}` response: `{1}`".format(market_data.get("58", ""), market_data))

        price = (float(market_data["270"]) + STOCK_EXTRA) if "270" in market_data else DEFAULT_LKOH_STOCK_PRICE
        targ_qty = int(TARGET_CASH_QUANTITY // price)
        print("Price: {0} {1}, Targ quantity: {2}\n ".format(price, market_data.get("15", ""), targ_qty))

        order = [
            "35=D",                     # MsgType
            "11="+order_id,             # ClOrdID
            "54=1",                     # Side
            "21=1",                     # HandlInst
            "55=LUKOIL",                # Symbol
            "40=2",                     # OrdType
            "38="+str(targ_qty),        # OrderQty
            "44="+str(price),           # Price
            "22=8",                     # IDSource
            "48=LKOH",                  # SecurityID
            "1=L01-00000F00",           # Account
            # "109=E5",                 # ClientID
            "100=MOEX"]                 # ExDestination
        report = client.request(order)
        if "39" in report:
            if report["39"] != "8":
                print("Order successful. Status: {0}".format(report["39"]))
            else:
                print("Order rejected: `{0}` response: `{1}`".format(report["58"], report))
        else:
            sys.exit('NewOrderSingle failed: `{0}` response: `{1}` '.format(report.get("58", ""), report))

if __name__ == '__main__':
    main()
