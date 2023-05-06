from login import login_in_zerodha
from zerodha import Zerodha
from straddle import Straddle
import pandas as pd

#getting Kite object
kiteobj = login_in_zerodha('cjqx8u4zedif6m4i', 'y2q7xt151teakfs1qebnforcmouutekw',
                               'CS7249', 'QGe_@7A9',
                               '733SF4CUBDJIS7HKRA4LJWGM4HNIH5KB')

#create Zerodha class bject
zerodha = Zerodha(kiteobj)

#creating straddle object 
straddle_obj = Straddle(zerodha)

#fetch instruments
instruments = zerodha.get_instruments()








exit()
straddle_obj.position_taker()

kws.on_ticks   = zerodha.on_ticks
kws.on_connect = zerodha.on_connect
kws.on_close   = zerodha.on_close

