import pandas as pd
import time

class Straddle:

    def __init__(self, zerodha, tick_transfer, order_update) -> None:
        
        self.put_position    = 0
        self.put_sl          = 0.15
        self.put_sl_val      = None
        self.put_option      = None
        self.put_token       = 0
        self.put_price       = None

        self.call_position   = 0
        self.call_sl         = 0.15
        self.call_sl_val     = None
        self.call_option     = None
        self.call_token      = 0
        self.call_price      = None

        self.end_time        = None
        self.start_time      = None

        self.zerodha_obj     = zerodha

        self.optionsChainDF  = None

        self.EXIT_CONDITION  = False

        self.tick_transfer  = tick_transfer 
        self.order_update   = order_update

    def order_reciever(self):

        #run until exit condition is not satisfied
        while not self.EXIT_CONDITION: 

            #getting order
            order = self.order_update.get()
            print(order)

            #if the option is PUT option
            print(order['tradingsymbol'], type(order['tradingsymbol']))
            if (order['tradingsymbol'] == self.put_option) and (order['status'] == 'COMPLETE'):
                
                if order['transaction_type'] == 'SELL' :
                    self.put_option += -1
                    self.put_price = order['average_price']
                    self.put_SL_val = self.put_price * ( self.put_sl + 1)
                    print("call sl",self.call_SL_val)
                if order['transaction_type'] == 'BUY' :
                    self.put_option += 1 


            #if the option is CALL option
            elif (order['tradingsymbol'] == self.call_option) and (order['status'] == 'COMPLETE'):
                
                if order['transaction_type'] == 'SELL' :
                    self.call_option += -1
                    self.call_price = order['average_price']
                    self.put_SL_val = self.put_price * ( self.put_sl + 1)
                    print("put sl",self.put_SL_val)
                if order['transaction_type'] == 'BUY' :
                    self.call_option += 1 

    def tick_reciever(self):
        while not self.EXIT_CONDITION: 
            ticks = self.tick_transfer.get()
            for tick in ticks:
                #print(tick)
                pass
                # iterate through ticks
                #  if call_tick:
                ##  if call position is -1
                ###   check if sl hit ? --> exit and wait for position to change else throw error
                #  if put_tick:
                ##  if put position is -1
                ###   check if sl hit ? --> exit and wait for position to change else throw error

                #check for any open positions
                #close them
                
    
    def position_taker(self):
        
        # wait for start time
        while True:
            current_time = time.localtime()
            if (current_time.tm_hour > 9
                or (current_time.tm_hour == 9 and current_time.tm_min > 19)
                or (current_time.tm_hour == 9 and current_time.tm_min == 19 and current_time.tm_sec >= 30)):
                break
            time.sleep(1)
                
        # calculate BNF level
        symbol = "NSE:NIFTY BANK"
        BNF_LEVEL = self.zerodha_obj.get_LTP(instruments=[symbol])['NSE:NIFTY BANK']['last_price']

        # rounding up or down
        if BNF_LEVEL % 100 >= 50:
            ADJ_BNF_LEVEL = (BNF_LEVEL  +(100 - BNF_LEVEL  % 100))
        elif BNF_LEVEL % 100 < 50:
            ADJ_BNF_LEVEL = BNF_LEVEL -(BNF_LEVEL % 100)

        #calculating CALL strike
        CALL_strike = ADJ_BNF_LEVEL + 100
        #fetching CALL option
        self.call_option = self.optionsChainDF [(self.optionsChainDF ['instrument_type'].str.contains('CE')) & (self.optionsChainDF ['strike'] == CALL_strike)]['tradingsymbol']
        self.call_token  = self.optionsChainDF [(self.optionsChainDF ['instrument_type'].str.contains('CE')) & (self.optionsChainDF ['strike'] == CALL_strike)]['instrument_token']

        #calculating PUT strike
        PUT_strike = ADJ_BNF_LEVEL - 100
        #fetching PUT option
        self.put_option = self.optionsChainDF [(self.optionsChainDF ['instrument_type'].str.contains('PE')) & (self.optionsChainDF ['strike'] == PUT_strike)]['tradingsymbol']
        self.put_token  = self.optionsChainDF [(self.optionsChainDF ['instrument_type'].str.contains('PUT')) & (self.optionsChainDF ['strike'] == PUT_strike)]['instrument_token']
        #placing sell order for CALL
        self.zerodha_obj.place_order(tradingsymbol=self.call_option, transaction_type='SELL')

        #placing sell order for PUT
        self.zerodha_obj.place_order(tradingsymbol=self.put_option, transaction_type='SELL')

        #confirm if got sold
        while self.put_position != -1 and self.call_position != -1:
            print("waiting for position to be initiated")
            time.sleep(0.5)

    def latest_expiry_options_chain(self):

        #fetch instruments
        instruments = self.zerodha_obj.get_instruments()
        
        #converting to dataframe
        df = pd.DataFrame(instruments)
        
        #filtering out all non BANK NIFTY options instruments
        df = df[df['tradingsymbol'].str.contains('BANKNIFTY') & (df['instrument_type'].str.contains('PE') | df['instrument_type'].str.contains('CE'))]
        
        #picking up minimum expiry date
        minimumExpiryDate = min(df['expiry'])
        
        #filtering out all non minimum expiry date options
        self.optionsChainDF  = df[df['expiry'] == minimumExpiryDate]
    
