import pandas as pd
import time
import datetime

class Straddle:

    def __init__(self, zerodha, tick_transfer, order_update, parameters) -> None:
        
        self.put_position    = 0
        self.put_sl          = parameters['sl_percentage']
        self.put_sl_val      = None
        self.put_option      = None
        self.put_token       = 0
        self.put_price       = None

        self.call_position   = 0
        self.call_sl         = parameters['sl_percentage']
        self.call_sl_val     = None
        self.call_option     = None
        self.call_token      = 0
        self.call_price      = None

        self.zerodha_obj     = zerodha

        self.optionsChainDF  = None

        self.strike          = int(parameters['strike'])

        self.entry_time      = parameters['entry_time'].split(':')  
        self.EXIT_CONDITION  = False
        self.exit_time_list  = parameters['exit_time'].split(':')   
        self.exit_time       = datetime.datetime(2023, 5, 11, int(self.exit_time_list[0]), int(self.exit_time_list[1]), int(self.exit_time_list[2])).time()

        self.tick_transfer  = tick_transfer 
        self.order_update   = order_update

    def order_reciever(self):

        #run until exit condition is not satisfied
        while not self.EXIT_CONDITION: 

            #getting order
            order = self.order_update.get()
    
            #if the option is PUT option
           
            if (str(order['tradingsymbol']) == self.put_option) and (str(order['status']) == 'COMPLETE'):
            
                if str(order['transaction_type']) == 'SELL':
                    self.put_position  += -1
                    self.put_price     = float(order['average_price'])
                    self.put_sl_val    = self.put_price * ( self.put_sl + 1)
                    print("put sl",self.put_sl_val)

                if order['transaction_type'] == 'BUY':
                    self.put_position += 1 


            #if the option is CALL option
            elif (str(order['tradingsymbol']) == self.call_option) and (str(order['status'])  == 'COMPLETE'):

                if str(order['transaction_type']) == 'SELL' :
                    self.call_position  += -1
                    self.call_price     = float(order['average_price'])
                    self.call_sl_val    = self.call_price * ( self.call_sl + 1)
                    print("call sl",self.call_sl_val)

                if order['transaction_type'] == 'BUY' :
                    self.call_position += 1 

    def tick_reciever(self):
        while not self.EXIT_CONDITION: 
            ticks = self.tick_transfer.get()
            for tick in ticks:
                # CALL side SL check
                if int(tick['instrument_token']) == self.call_token and self.call_position == -1:
                    if float(tick['last_price']) >= self.call_sl_val:
                        print('CALL sl hit')
                        self.zerodha_obj.place_order(tradingsymbol=self.call_option, transaction_type='BUY')

                        while self.call_position != 0:
                            time.sleep(0.25)
                            
                # PUT side SL check
                if int(tick['instrument_token']) == self.put_token and self.put_position == -1:
                    if float(tick['last_price']) >= self.put_sl_val:
                        print('PUT sl hit')
                        self.zerodha_obj.place_order(tradingsymbol=self.put_option, transaction_type='BUY')

                        while self.put_position != 0:
                            time.sleep(0.25)

        #exit out any open position on time end
        if self.call_position == -1:
            self.zerodha_obj.place_order(tradingsymbol=self.call_option, transaction_type='BUY')

        if self.put_position == -1:
            self.zerodha_obj.place_order(tradingsymbol=self.put_option, transaction_type='BUY')


    def exit_condition_checker(self):

        #getting current seconds
        current_time    = datetime.datetime.now()
        current_seconds = (current_time.hour * 3600) + (current_time.minute * 60) + current_time.second

        #converting exit time into seconds
        exit_seconds    = (self.exit_time.hour * 3600) + (self.exit_time.minute * 60) + self.exit_time.second
        print(current_seconds, exit_seconds, "seconds")

        #sleeping for remainder of time
        time.sleep(exit_seconds - current_seconds)
        self.EXIT_CONDITION  = True

    def position_taker(self):
        
        # wait for start time
        while True:
            current_time = time.localtime()
            if (current_time.tm_hour > int(self.entry_time[0])
                or (current_time.tm_hour == int(self.entry_time[0]) and current_time.tm_min > int(self.entry_time[1]))
                or (current_time.tm_hour == int(self.entry_time[0]) and current_time.tm_min == int(self.entry_time[1]) and current_time.tm_sec >= int(self.entry_time[2]))):
                break
            time.sleep(0.12)
                
        # calculate BNF level
        symbol = "NSE:NIFTY BANK"
        BNF_LEVEL = self.zerodha_obj.get_LTP(instruments=[symbol])['NSE:NIFTY BANK']['last_price']

        # rounding up or down
        if BNF_LEVEL % 100 >= 50:
            ADJ_BNF_LEVEL = (BNF_LEVEL  +(100 - BNF_LEVEL  % 100))
        elif BNF_LEVEL % 100 < 50:
            ADJ_BNF_LEVEL = BNF_LEVEL -(BNF_LEVEL % 100)

        #calculating CALL strike
        CALL_strike = ADJ_BNF_LEVEL + self.strike 
        #fetching CALL option
        self.call_option = str(self.optionsChainDF[(self.optionsChainDF ['instrument_type'].str.contains('CE')) & (self.optionsChainDF ['strike'] == CALL_strike)]['tradingsymbol'].values[0])
        self.call_token  = int(self.optionsChainDF[(self.optionsChainDF ['instrument_type'].str.contains('CE')) & (self.optionsChainDF ['strike'] == CALL_strike)]['instrument_token'].values[0])

        #calculating PUT strike
        PUT_strike = ADJ_BNF_LEVEL - self.strike 
        #fetching PUT option
        self.put_option = str(self.optionsChainDF[(self.optionsChainDF ['instrument_type'].str.contains('PE')) & (self.optionsChainDF ['strike'] == PUT_strike)]['tradingsymbol'].values[0])
        self.put_token  = int(self.optionsChainDF[(self.optionsChainDF ['instrument_type'].str.contains('PE')) & (self.optionsChainDF ['strike'] == PUT_strike)]['instrument_token'].values[0])
        
        print(self.put_token, self.call_token)
        #placing sell order for CALL
        self.zerodha_obj.place_order(tradingsymbol=self.call_option, transaction_type='SELL')

        #placing sell order for PUT
        self.zerodha_obj.place_order(tradingsymbol=self.put_option, transaction_type='SELL')

        #confirm if got sold
        while self.put_position != -1 and self.call_position != -1:
            print("waiting for position to be initiated",self.put_position,self.call_position)
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
    
