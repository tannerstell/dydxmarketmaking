import time
from dydx3 import Client, helpers
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_UP
from typing import Optional
import json

credentials = json.load(open("settings.json"))["credentials"]

private_client = Client(
    host='https://api.dydx.exchange',
    api_key_credentials=credentials["api_key_credentials"],
    stark_private_key=credentials["stark_private_key"]
)

class dydx:
    def __init__(self, market):
        self.market = market
        self.step_size, self.tick_size, self.min_order_size = self.get_market(self.market)

    @staticmethod
    def cancel_all(market, side:Optional[str] = None):
        if side == None:
            response = private_client.private.cancel_active_orders(market)
        else:
            response = private_client.private.cancel_active_orders(market, side)
        time.sleep(0.1)

    @staticmethod
    def cancel(id):
        private_client.private.cancel_order(id)
        time.sleep(0.1)
        return 0

    @staticmethod
    def api_time():
        response = private_client.public.get_time()
        time.sleep(0.1)
        return response

    def buy(self, size, price):
        expiration_seconds = (datetime.fromtimestamp(self.api_time().data['epoch']) + timedelta(seconds=300)).timestamp()
        response = private_client.private.create_order(
             position_id = credentials['position_id'],
             market = self.market,
             side = "BUY",
             order_type = "LIMIT",
             post_only = False,
             size = str(max(Decimal(self.truncate(self.step_size, size)), Decimal(self.min_order_size))),
             price = str(self.truncate(self.tick_size, price)),
             limit_fee = 0.1,
             time_in_force = "GTT",
             expiration_epoch_seconds=expiration_seconds).data
        time.sleep(0.2)
        return response["order"]["id"]

    def close(self, side, size, price, order_type):
        time.sleep(0.1)
        expiration_seconds = (datetime.fromtimestamp(self.api_time().data['epoch']) + timedelta(seconds=43200)).timestamp()
        placed_order = private_client.private.create_order(
            position_id=credentials['position_id'],  # required for creating the order signature
            market=self.market,
            side=side,
            price=str(self.truncate(self.tick_size, price)),
            order_type=order_type,
            trigger_price=str(self.truncate(self.tick_size, price)),
            reduce_only=True,
            post_only=False,
            size=str(self.truncate(self.step_size, size)),
            limit_fee='0.015',
            expiration_epoch_seconds=expiration_seconds,
            time_in_force="IOC",
        )
        return placed_order
    def sell(self, size, price):
        expiration_seconds = (datetime.fromtimestamp(self.api_time().data['epoch']) + timedelta(seconds=300)).timestamp()
        response = private_client.private.create_order(
                     position_id = credentials['position_id'],
                     market = self.market,
                     side = "SELL",
                     order_type = "LIMIT",
                     post_only = False,
                     size = str(max((self.truncate(self.step_size, size)), Decimal(self.min_order_size))),
                     price = str(self.truncate(self.tick_size, price)),
                     limit_fee = 0.1,
                     time_in_force = "GTT",
                     expiration_epoch_seconds = expiration_seconds).data
        time.sleep(0.2)
        return response["order"]["id"]

    @staticmethod
    def truncate(increment_size, value):
        increment_size, value = Decimal(increment_size), abs(Decimal(value))
        new_value = (value//increment_size)*increment_size
        new_value = Decimal(abs(new_value)).quantize(Decimal(increment_size), rounding=ROUND_UP)
        return new_value

    @staticmethod
    def get_price(market):
        response = private_client.public.get_orderbook(market).data
        price = float(response['asks'][0]['price'])
        time.sleep(0.1)
        return price

    @staticmethod
    def get_account(market):
        response = private_client.private.get_account(credentials["default_ethereum_address"]).data['account']
        positions = response['openPositions']
        equity = float(response['equity'])
        value = float(sum([abs(float(position['size']))*float(position['entryPrice']) for position in positions.values()]))
        leverage = value/equity
        time.sleep(0.1)
        try:
            p = positions[market]
            size = p['size']
            unrealized_pnl = float(p['unrealizedPnl'])
            realized_pnl = float(p['realizedPnl'])
            entryPrice = float(p['entryPrice'])
            side = p['side']
            p = [size, unrealized_pnl, realized_pnl, entryPrice, side]
            return leverage, equity, p
        except:
            return leverage, equity, [0,0,0,0,""]

    @staticmethod
    def get_market(market):
        response = private_client.public.get_markets(market=market).data['markets'][market]
        step_size = response['stepSize']
        tick_size = response['tickSize']
        min_order_size = response['minOrderSize']
        time.sleep(0.1)
        return step_size, tick_size, min_order_size

    @staticmethod
    def get_positions(market):
        time.sleep(0.1)
        try:
            response = private_client.private.get_positions(market).data['positions'][0]
            if response['status']=="OPEN":
                size = response['size']
                unrealized_pnl = float(response['unrealizedPnl'])
                realized_pnl = float(response['realizedPnl'])
                entryPrice = float(response['entryPrice'])
                side = response['side']
                return entryPrice, size, unrealized_pnl, realized_pnl, side
            else:
                return 0,0,0,0,""
        except:
            return 0,0,0,0,""

    @staticmethod
    def get_orders(market, order_type:Optional[str] = None):
        if order_type == None:
            order_type = 'LIMIT'
        response = private_client.private.get_orders(market, order_type=order_type).data['orders']
        total_order_size = 0
        orders = []
        try:
            for order in response:
                if order["status"] == "OPEN":
                    order_price = float(order["price"])
                elif order["status"] == 'UNTRIGGERED':
                    order_price = float(order["triggerPrice"])
                order_size = float(order["remainingSize"])
                order_side = order["side"]
                order_type = order['type']
                order_id = order["id"]
                total_order_size+=order_size
                orders.append([order_price, order_size, order_side, order_type, order_id])
        except:
            return 0, [0,0,"", order_type, ""]
        time.sleep(0.1)
        return total_order_size, orders

# d = dydx("BTC-USD").close("SELL", 0.01, "36561", "STOP_MARKET")
