from fix_client import *

def main():
    with socket.socket() as adaptorSock:
        adaptorSock.connect(('127.0.0.1', 5002))
        client = FixClient(adaptorSock, "49=TEST", "56=QUIK")

        logon = ["35=A","1=L01-00000F00", "141=Y", "109=E5", "98=0", "108=53"]
        market_request = ["35=V", "262=256", "263=1", "264=1", "265=1", "267=1", "269=0", "146=1",
            "22=8", "48=LKOH", "100=MOEX"]
        order = [
            "35=D",             # MsgType
            "11=129",           # ClOrdID
            "54=1",             # Side
            "21=1",             # HandlInst
            "40=1",             # OrdType
            "152=100000",       # CashOrderQty
            # "38=29",            # OrderQty
            # "44=4600",          # Price
            "22=8",             # IDSource
            "48=LKOH",          # SecurityID
            "1=L01-00000F00",   # Account
            "109=E5",           # ClientID
            "100=MOEX"]

        logon_resp = client.request(logon)
        print ('Logon response: ' + str(logon_resp))

        mdr_resp = client.request(market_request)
        print ('MarketDataRequest response: ' + str(mdr_resp))
        if "270" in mdr_resp:
            print ("Price of the Market Data Entry: " + str(mdr_resp["270"]))

        # order_reps = client.request(order)
        # print ('New Order Single: ' + str(order_reps))


if __name__ == '__main__':
    main()