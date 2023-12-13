import data
import api
import time
from decimal import Decimal

class algorithm:
    def __init__(self, market, max_leverage, l_num_orders, s_num_orders, l_order_pct, s_order_pct, l_spacing_sd, s_spacing_sd, inc, l_multiplier, s_multiplier, tp_pct):
        self.market = market
        self.max_leverage = max_leverage
        self.l_num_orders = l_num_orders
        self.s_num_orders = s_num_orders
        self.inc = inc
        self.l_order_pct = l_order_pct
        self.s_order_pct = s_order_pct
        self.l_spacing_sd = l_spacing_sd
        self.s_spacing_sd = s_spacing_sd
        self.l_multiplier = l_multiplier
        self.s_multiplier = s_multiplier
        self.tp_pct = tp_pct
        self.dydx = api.dydx(self.market)
        self.step_size, self.tick_size, self.min_order_size = Decimal(self.dydx.step_size), Decimal(self.dydx.tick_size), Decimal(self.dydx.min_order_size)
        self.max_step = self.min_order_size/self.step_size
    def ladder(self, l_multiplier):
        lband, mband, hband, std_dev = data.keltner(self.market, l_multiplier)
        laddered_prices = {"asks": [[hband+std_dev*(self.s_multiplier-self.l_multiplier), self.s_order_pct]],
                           "bids":[[lband, self.l_order_pct]]}
        s_order_pct, l_order_pct = self.s_order_pct, self.l_order_pct
        for i in range(1, max(self.l_num_orders, self.s_num_orders)):
            last_ask, last_bid = laddered_prices["asks"][-1][0], laddered_prices["bids"][-1][0]
            if i<self.s_num_orders:
                laddered_prices["asks"].append([last_ask+self.s_spacing_sd*std_dev, s_order_pct])
                s_order_pct *= self.inc
            if i<self.l_num_orders:
                laddered_prices["bids"].append([last_bid-self.l_spacing_sd*std_dev, l_order_pct])
                l_order_pct*=self.inc
        return laddered_prices
    def execution(self):
        print("Starting algorithm on " + self.market)
        while True:
            try:
                leverage, equity, positions = self.dydx.get_account(self.market)
                size, unrealized, realized, entry, side = positions
                f_size, pnl = abs(float(size)), sum([unrealized, realized])
                total_order_size, orders = self.dydx.get_orders(self.market, "TAKE_PROFIT_MARKET")
                try:
                    tp_orders = [[order[0], order[1], order[2]] for order in orders]
                    self.dydx.cancel_all(self.market)
                    if f_size>0:
                        [self.dydx.close(order[2], order[1], order[0], "TAKE_PROFIT_MARKET") for order in tp_orders]
                except:
                    pass
                current_price = api.dydx.get_price(self.market)
                lband, mband, hband, std_dev = data.keltner(self.market, self.l_multiplier)
                if side == "LONG":
                    new_entry = current_price - (pnl / f_size) if pnl >= 0 else current_price + abs(pnl / f_size)
                    if total_order_size<f_size:
                        order_id = self.dydx.close("SELL", f_size-total_order_size+float(self.min_order_size), max(entry*(1+self.tp_pct), mband-0.2*(mband-new_entry), current_price*1.0001), "TAKE_PROFIT_MARKET")
                elif side == "SHORT":
                    new_entry = current_price + (pnl / f_size) if pnl >= 0 else current_price - abs(pnl / f_size)
                    if total_order_size<f_size:
                        order_id = self.dydx.close("BUY", f_size - total_order_size, min(entry*(1-self.tp_pct), 0.2*(new_entry-mband)+mband, current_price*0.999), "TAKE_PROFIT_MARKET")
                if leverage<self.max_leverage:
                    try:
                        if leverage>=1 and leverage<2:
                            laddered_prices = self.ladder(self.l_multiplier+1)
                            quantity_multiplier = 0.75
                        elif leverage>=2 and leverage<3:
                            laddered_prices = self.ladder(self.l_multiplier+2)
                            quantity_multiplier = 0.5
                        elif leverage >= 3 and leverage < 4:
                            laddered_prices = self.ladder(self.l_multiplier+3)
                            quantity_multiplier = 0.4
                        else:
                            laddered_prices = self.ladder(self.l_multiplier)
                            quantity_multiplier = 1
                        asks, bids = laddered_prices["asks"], laddered_prices["bids"]
                        if side == "SHORT":
                            entry = current_price + (pnl / f_size) if pnl >= 0 else current_price - abs(pnl / f_size)
                        elif side == "LONG":
                            entry = current_price - (pnl / f_size) if pnl >= 0 else current_price + abs(pnl / f_size)
                        else:
                            entry = 0
                        for i in range(len(max(bids, asks))):
                            if i<len(bids) and self.l_num_orders!=0:
                                b_price, b_order_pct_equity = bids[i]
                                if (b_price<entry-std_dev/2 and entry!=0) or entry == 0:
                                    b_quantity = ((equity * b_order_pct_equity) / b_price) * quantity_multiplier
                                    self.dydx.buy(b_quantity, b_price)
                            if i<len(asks) and self.s_num_orders!=0:
                                a_price, a_order_pct_equity = asks[i]
                                if (a_price>entry+std_dev/2 and entry!=0) or entry == 0:
                                    a_quantity = ((equity * a_order_pct_equity) / a_price) * quantity_multiplier
                                    self.dydx.sell(a_quantity, a_price)
                    except Exception as e:
                        print(e)
                        pass
                time.sleep(60)
            except:
                pass
# algorithm("SNX-USD",1,1,5,3,0.01,1,1,1.1, 2,3, 0.01).execution()
