import sys
import ipaddress
import time
from fix_client import FixClient, Tags


def main():
    if len(sys.argv) != 2:
        sys.exit("Error: need to pass adapter port as argument.")
    port = int(sys.argv[1])

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
            if "270" in market_data:
                print("Price: {0} {1}\n ".format(market_data["270"], market_data.get("15", "")))
        else:
            sys.exit("MarketDataRequest failed: `{0}` response: `{1}`".format(market_data.get("58", ""), market_data))

        order = [
            "35=D",             # MsgType
            "11=129",           # ClOrdID
            "54=1",             # Side
            "21=1",             # HandlInst
            "55=LUKOIL",        # Symbol

            "40=1",             # OrdType
            #"152=100000",       # CashOrderQty
            "38=29",            # OrderQty
            "44=4600",          # Price

            "22=8",             # IDSource
            "48=LKOH",          # SecurityID
            "1=L01-00000F00",   # Account
            "109=E5",           # ClientID
            "100=MOEX"]
        report = client.request(order)
        if "39" in report:
            if report["39"] != "8":
                print("Order status: " + report["39"])
            else:
                print("Order rejected: `{0}` response: `{1}`".format(report["58"], str(report)))
        else:
            sys.exit('NewOrderSingle failed: `{0}` response: `{1}` '.format(report.get("58", ""), report))

        # print(client.recv())


if __name__ == '__main__':
    main()
