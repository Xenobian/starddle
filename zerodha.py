class Zerodha:

    def __init__(self, kiteObj) -> None:
        self.kiteObj = kiteObj

    def get_instruments(self):
        return self.kiteObj.instruments(exchange='NFO')
    
    def get_LTP(self,instruments):
        return self.kiteObj.ltp(instruments)

    def place_order(self, tradingsymbol, transaction_type):

        try:
            order_id = self.kiteObj.place_order(variety=self.kiteObj.VARIETY_REGULAR,
                        tradingsymbol=tradingsymbol,
                        exchange=self.kiteObj.EXCHANGE_NFO,
                        transaction_type=transaction_type,
                        quantity=25,
                        order_type=self.kiteObj.ORDER_TYPE_MARKET,
                        product=self.kiteObj.PRODUCT_MIS,
                        validity=self.kiteObj.VALIDITY_DAY)

            #logging.info("Order placed. ID is: {}".format(order_id))

        except Exception as e:
            #logging.info("Order placement failed: {}".format(e.message)
            pass

    def on_ticks(ws, ticks):
        # Callback to receive ticks.
        #logging.debug("Ticks: {}".format(ticks))
        pass

    def on_connect(self, ws, response):
        # Callback on successful connect.
        # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
        ws.subscribe([738561, 5633])

        # Set RELIANCE to tick in `full` mode.
        ws.set_mode(ws.MODE_FULL, [738561])

    def on_close(self, ws, code, reason):
        # On connection close stop the event loop.
        # Reconnection will not happen after executing `ws.stop()`
        ws.stop()