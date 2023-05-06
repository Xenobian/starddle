import pandas as pd

class Straddle:

    def __init__(self, zerodha) -> None:
        
        self.put_position    = None
        self.put_sl          = None
        self.put_option      = None

        self.call_position   = None
        self.call_sl         = None
        self.call_option     = None

        self.end_time        = None
        self.start_time      = None

        self.zerodha_obj     = zerodha

        self.optionsChainDF  = None

    def order_reciever(self):
        #if call_position is 0 and call sell successful recieved
        ## set the position to -1
        ##elif put_position is 0 and put sell successful recieved
        ## set the position to -1

        ##elif call position is -1 and buy order
        # change pos to 0

        ##elif put position is -1 and buy order
        # change pos to 0
        pass

    def tick_reciever(self):
        #while loop till exit time
        # iterate through ticks
        #  if call_tick:
        ##  if call position is -1
        ###   check if sl hit ? --> exit and wait for position to change else throw error
        #  if put_tick:
        ##  if put position is -1
        ###   check if sl hit ? --> exit and wait for position to change else throw error

        #check for any open positions
        #close them
        pass
    
    def position_taker(self):

        # calculate BNF level
        symbol = "NSE:NIFTY BANK"
        BNF_LEVEL = self.zerodha.get_LTP(instruments=[symbol])['NSE:NIFTY BANK']['last_price']

        # rounding up or down
        if BNF_LEVEL % 100 >= 50:
            ADJ_BNF_LEVEL = (BNF_LEVEL  +(100 - BNF_LEVEL  % 100))
        elif BNF_LEVEL % 100 < 50:
            ADJ_BNF_LEVEL = BNF_LEVEL -(BNF_LEVEL % 100)

        #calculating CALL strike
        CALL_strike = ADJ_BNF_LEVEL + 100
        #fetching CALL option
        call_option = self.optionsChainDF [(self.optionsChainDF ['instrument_type'].str.contains('CE')) & (self.optionsChainDF ['strike'] == CALL_strike)]['tradingsymbol']

        #calculating PUT strike
        PUT_strike = ADJ_BNF_LEVEL - 100
        #fetching PUT option
        put_option = self.optionsChainDF [(self.optionsChainDF ['instrument_type'].str.contains('PE')) & (self.optionsChainDF ['strike'] == PUT_strike)]['tradingsymbol']

        #placing sell order for CALL
        self.zerodha.place_order(tradingsymbol=call_option, transaction_type=self.zerodha.TRANSACTION_TYPE_SELL)

        #placing sell order for PUT
        self.zerodha.place_order(tradingsymbol=put_option, transaction_type=self.zerodha.TRANSACTION_TYPE_SELL)

        #confirm if got sold
        
    def latest_expiry_options_chain(self):

        #fetch instruments
        instruments = self.zerodha.get_instruments()
        
        #converting to dataframe
        df = pd.DataFrame(instruments)
        
        #filtering out all non BANK NIFTY options instruments
        df = df[df['tradingsymbol'].str.contains('BANKNIFTY') & (df['instrument_type'].str.contains('PE') | df['instrument_type'].str.contains('CE'))]
        
        #picking up minimum expiry date
        minimumExpiryDate = min(df['expiry'])
        
        #filtering out all non minimum expiry date options
        self.optionsChainDF  = df[df['expiry'] == minimumExpiryDate]
    
