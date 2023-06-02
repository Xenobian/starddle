from login import Login
from zerodha import Zerodha
from straddle import Straddle
from kiteconnect import KiteTicker
import time
import queue
import threading
import json

#creating data transfer queues
tick_transfer = queue.Queue()
order_update  = queue.Queue()

#importing config
file = open('conf.json')
parameters = json.load(file)

login = Login(parameters['account'])
#generating request token
login.generate_request_token()
#creating kite object
kiteObj = login.generate_kite_object()
#creating Ticker object
kws = login.generate_ticker()

#create Zerodha class bject
zerodha = Zerodha(kiteObj, tick_transfer, order_update )

#creating straddle object 
straddle = Straddle(zerodha, tick_transfer, order_update, parameters['straddle'])

#create options chain
straddle.latest_expiry_options_chain()

#assigning callback functions
kws.on_ticks        = zerodha.on_ticks
kws.on_connect      = zerodha.on_connect
kws.on_close        = zerodha.on_close
kws.on_order_update = zerodha.on_order_update

#starting tick reciever, order reciever thread
tick_reciever_thread = threading.Thread(target=straddle.tick_reciever)
tick_reciever_thread.start()
order_update_thread = threading.Thread(target=straddle.order_reciever)
order_update_thread .start()

#starting kite ticker in Threadded mode
kws.connect(threaded=True)

#wait for ticker to initialize properly
time.sleep(1)

#initiate inital position
straddle.position_taker()

kws.subscribe([straddle.call_token,straddle.put_token]) 

#Wait for exit time
straddle.exit_condition_checker()

#closing out threads
tick_reciever_thread.join()
order_update_thread .join()

print("Finished execution")







