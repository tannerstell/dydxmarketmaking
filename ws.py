import time
import websocket
import api
from dydx3 import Client
import json
import queue
import threading
import data
import numpy
import pygame
pygame.mixer.init()
enter_trade_sound = "enter.mp3"
exit_trade_sound = "exit.mp3"
message_queue = queue.Queue()
credentials = json.load(open("settings.json"))["credentials"]
client = Client(
        host = "wss://api.dydx.exchange/v3/ws",
        default_ethereum_address= credentials["default_ethereum_address"],
        api_key_credentials=credentials["api_key_credentials"],
        stark_private_key=credentials["stark_private_key"]
    )

def on_message(ws, message):
    try:
        message_queue.put(json.loads(message))
    except Exception as e:
        print(e)
        pass

def on_error(ws, error):
    print(error+ " closing websocket.")
    time.sleep(0.2)
    ws.close()
    main()

def on_close(ws, close_status_code, close_msg):
    print(close_msg)
    time.sleep(0.2)
    main()

i = 0
def on_open(ws):

    iso = api.dydx.api_time().data['iso']

    signature = client.private.sign(
        request_path='/ws/accounts',
        method='GET',
        iso_timestamp=iso,
        data={}
    )

    req = {
        'type' : 'subscribe',
        'channel': "v3_accounts",
        'accountNumber': '0',
        'apiKey' : credentials["api_key_credentials"]["key"],
        "passphrase" : credentials["api_key_credentials"]["passphrase"],
        'timestamp' : iso,
        'signature' : signature
}
    ws.send(json.dumps(req))
    print("Opened connection")
def message_tasks():
    while True:
        try:
            message = message_queue.get(timeout=2)
            fills = message["contents"]["fills"]
            if len(fills) > 0:
                for fill in fills:
                    side, market, price, size, type = fill["side"], fill["market"], float(fill["price"]), fill["size"], fill["type"]
                    entryPrice, position_size, unrealized_pnl, realized_pnl, position_side = api.dydx.get_positions(market)
                    f_size = abs(float(size))
                    if side == "BUY":
                        if type!="TAKE_PROFIT_MARKET" and type!= "TAKE_PROFIT_LIMIT":
                            print("{}: Filled {}: ${}".format(market, side, numpy.round(price * f_size, 4)))
                            pygame.mixer.Sound(enter_trade_sound).play()
                            # api.dydx(market).close("SELL", size, price-50, "STOP_MARKET")
                            response = api.dydx(market).close("SELL", size, price*1.016, "TAKE_PROFIT_MARKET")
                        else:
                            print(market + ": Profit: ${}".format(numpy.round((price-price/1.005)*f_size, 4)))
                            pygame.mixer.Sound(exit_trade_sound).play()

                    if side == "SELL":
                        if type!="TAKE_PROFIT_MARKET" and type!= "TAKE_PROFIT_LIMIT":
                            response = api.dydx(market).close("BUY", size, price*0.995,"TAKE_PROFIT_MARKET")
                            print("{}: Filled {}: ${}".format(market, side, numpy.round(price * f_size, 4)))
                            pygame.mixer.Sound(enter_trade_sound).play()
                        else:
                            print(market + ": Profit: ${}".format(numpy.round((price-price/1.005)*f_size, 4)))
                            pygame.mixer.Sound(exit_trade_sound).play()
                        pass
        except Exception as e:
            pass

def main():
    try:
        ws = websocket.WebSocketApp("wss://api.dydx.exchange/v3/ws",
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        print("Connecting to websocket")
        processing_thread = threading.Thread(target=message_tasks)
        processing_thread.daemon = True
        processing_thread.start()
        ws.run_forever(ping_interval=30)
    except:
        pass
# main()
