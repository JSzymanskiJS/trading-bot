from binance.client import Client
from binance.enums import *
import binancealgorithm as ba
import config
import numpy as np
import json, websocket, pprint, os, datetime, asyncio, pickle, time, math
import variablefunctionanalysis as vfa
import mydataclasses as dc

STOP_TIME = 0.105
SIZE_OF_BLUR_KERNEL = 30
EXCHANGE_TYPE = ['BNBUSDT', 'ONEUSDT', 'AAVEUSDT']
is_testing = True #TODO
working_exchange_type = EXCHANGE_TYPE.copy()
trading_info = dc.TradingInformation()
EXCHANGE_TYPES = []
client = Client(config.API_KEY, config.API_SECRET)

try:
    message = client.get_exchange_info()
    time.sleep(STOP_TIME)
    trading_info.save_exchange_info(message)
except Exception as e:
    print(e)

exchange_info = trading_info.load_exchange_info()

for row in exchange_info:
    for trade_pair in working_exchange_type:
        if row['symbol'] == trade_pair:
            EXCHANGE_TYPES.append(row)
            working_exchange_type.remove(trade_pair)

SOCKET = "wss://stream.binance.com:9443/"

if len(EXCHANGE_TYPE) == 1:
    SOCKET += "ws/" + EXCHANGE_TYPE[0].lower() + "@trade"
    is_multipule_traiding_pair = False
elif len(EXCHANGE_TYPE) > 1:
    SOCKET += "stream?streams="
    for exch_type in EXCHANGE_TYPE:
        if exch_type == EXCHANGE_TYPE[-1]:
            SOCKET += exch_type.lower() + "@trade"   
        else:
            SOCKET += exch_type.lower() + "@trade" + "/"
    is_multipule_traiding_pair = True
else:
    SOCKET = None

binAlg = {}
asset_data = {}
wallet = {}
ballances = {}
for trade_pair in EXCHANGE_TYPES:
    var = client.get_asset_balance(trade_pair['quoteAsset'])
    time.sleep(STOP_TIME)
    ballances[trade_pair['quoteAsset']] = float(var['free'])
 
can_execute = dc.Waiter()
execution_amout = dc.Counter()

async def can_execute_function(delay = STOP_TIME):
    can_execute.can_do = False
    await asyncio.sleep(delay)
    can_execute.can_do = True

def on_open(ws):
    print('opened connection')
    for trade_pair in EXCHANGE_TYPE:
        #Optional
        #binAlg[trade_pair].loadTradingData("/WorkingData/BTCUSDT/1613757661.199958_data_file.pkl")
        choice = input("Do you want to load trading data for " + trade_pair +"? (Write 'y' for Yes or anything else for No): ")
        if choice == 'y':
            choice = input("Enter name of file to load data: ")

            path = os.getcwd() + "/WorkingData/" + trade_pair + "/" + choice
            oldClient = binAlg[trade_pair].client
            
            try:
                read_file = open(path, "rb")
                binAlg[trade_pair] = pickle.load(read_file) 
                binAlg[trade_pair].client = oldClient
                print("Data for '{}' has been successfully updated from pikled file.".format(trade_pair))
            except IOError:
                print('Error: File does not appear to exist.')
        else:
            #Wallets creation
            for trade_pair_1 in EXCHANGE_TYPES:
                if trade_pair_1['symbol'] == trade_pair:
                    base_MG_type = trade_pair_1['baseAsset']
                    quote_MG_type = trade_pair_1['quoteAsset']
                    
                    base_MG = client.get_asset_balance(base_MG_type)
                    base_MG = float(base_MG['free'])
                    time.sleep(STOP_TIME)
                    
                    if quote_MG_type == 'XRP' or 'USDT' or 'TUSD' or 'BUSD' or 'USDC' or 'TRX' or 'BIDR' or 'IDRT' or 'BVND' or 'ETH' or 'BTC' or 'BNB':
                        pass
                    else:
                        print(quote_MG_type + " -> This is NOT a cryptocurrency nor stablecoin - this is FIAT in its Purest form. It will be taxed!!!")
                        
                    for filter_ in trade_pair_1['filters']:
                        if filter_['filterType'] == 'MIN_NOTIONAL':
                            min_order_value = float(filter_['minNotional'])*1.07
                        elif filter_['filterType'] == 'LOT_SIZE':
                            base_MG_precision = float(filter_['minQty'])
                        elif filter_['filterType'] == 'PRICE_FILTER':
                            price_precision = float(filter_['minPrice'])
                    
                    max_amount_of_steps = int(math.floor(ballances[quote_MG_type] / (min_order_value)))
                    if min_order_value != None:        
                        print("Quote material goods for this exchage pair (" + trade_pair + ") is " + quote_MG_type + ".")
                        print("You have {} of {}. You can NOT cross {}.".format(ballances[quote_MG_type], quote_MG_type, max_amount_of_steps))
                        
                        choice = int(input("How many steps do you consider? Please write it to me :) : "))
                        
                        if choice < max_amount_of_steps:
                            max_amount_of_steps = choice
                        
                        ballances[quote_MG_type] -= max_amount_of_steps * (min_order_value)
                        
                        wallet[trade_pair] = dc.Wallet(base_MG_type=base_MG_type, base_MG=base_MG, base_MG_precision=base_MG_precision, quote_MG_type=quote_MG_type, quote_MG=max_amount_of_steps * min_order_value, min_order_value=min_order_value, price_precision=price_precision, max_amount_of_steps=max_amount_of_steps)
                        dictionary = wallet[trade_pair].__dict__()
                        print(dictionary)   
                        print("You have {} of {} left.\n".format(ballances[quote_MG_type], quote_MG_type))
                    else:
                        print('ERROR - invalid quoteAsset type!')
        #Creating algorithnic objects for trade pairs
        binAlg[trade_pair] = ba.BinanceAlgorithm(client = client, exchange_type = trade_pair, 
                                                 bluring_kernel=vfa.generateDynamicGaussBluringKernel(SIZE_OF_BLUR_KERNEL), 
                                                 wallet=wallet[trade_pair])
        asset_data[trade_pair] = dc.DataFrame(trade_pair, 0.0, 0, 0.0)
                
    print("starting trading ")      
        
def on_close(ws):
    print('closed connection')
    for trade_pair in EXCHANGE_TYPE:
        binAlg[trade_pair].saveTradingData()
        binAlg[trade_pair].generateRaport()
            
def on_message(ws, message):
    json_message = json.loads(message)
    print(json_message)
    
    if is_multipule_traiding_pair:
        json_message = json_message['data']
    
    symbol = json_message['s']
    price = float(json_message['p'])
    time = int(json_message['T'])
    quantity = float(json_message['q'])
    
    asset_data[symbol].writeData(symbol, price, time, quantity)
    
    has_been_executed = binAlg[symbol].baseAlgorithm(asset_data_frame = asset_data[symbol], 
                                                     min_profit_percentage = 0.015, min_loss_percentage = 0.01, 
                                                     can_execute = can_execute.can_do)
    
    loop = asyncio.get_event_loop()
    if has_been_executed:
        execution_amout.how_much += 1
        if execution_amout.how_much <= 100000:
            loop.run_until_complete(can_execute_function())
        else:
            loop.run_until_complete(can_execute_function(0.5))
    
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()