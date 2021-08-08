from binance.client import Client
from binance.enums import *
import variablefunctionanalysis as vfa
import mydataclasses as dc
from colorama import Fore, Back, Style
import sys
import csv, json, datetime, os, copy, pickle, decimal



class BinanceAlgorithm:
    def __init__(self, client, exchange_type, exchange_rate = [], bluring_kernel = vfa.generateDynamicGaussBluringKernel(), wallet = dc.Wallet, name_of_data = None):
        self.client = client
        if name_of_data == None:
            self.name_of_data = exchange_type
        else:
            self.name_of_data = name_of_data
        self.exchange_type = exchange_type 
        self.wallet = wallet
        #Anlyzis Algorithm
        self.exchange_rate = exchange_rate
        self.is_changed_to_decreasing = False
        self.is_changed_to_rising = False
        self.is_profitable_to_sell = False
        self.is_profitable_to_buy = False
        self.delta_1 = 0
        self.delta_2 = 0
        self.exchange_rate_bought = []
        self.exchange_rate_1 = 0
        self.exchange_rate_2 = 0
        self.bluring_kernel = bluring_kernel
        self.min_selling_value = sys.float_info.max
        #Measuring data
        self.successful_purchases = 0
        self.successful_sells = 0
        self.analysed_data_frames = 0
        self.new_exchange_rate = 0
        self.min_wallet_price = self.wallet.quote_MG
        self.max_wallet_price = self.wallet.quote_MG
        self.min_asset_price = sys.float_info.max
        self.max_asset_price = sys.float_info.min
        self.starting_asset_price = None
        self.error_amount = 0
        self.starting_time = datetime.datetime.now()
        self.ending_time = None

#Data Managers       
    def saveTradingData(self): 
        parent = os.getcwd() + "/WorkingData/" + self.name_of_data
        child = "/" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + "_data_file.pkl"    
        if not os.path.exists(parent):
            os.makedirs(parent)
                    
        try:
            write_file = open(parent + child, "wb")
            pickle.dump(self, write_file)
            write_file.close()
        except IOError:
            print('Error: File can not be created.')
    '''      
    def loadTradingData(self, trading_data_path = str): #Deprecated/Don't work
        path = os.getcwd() + trading_data_path
        oldClient = self.client
        
        try:
            read_file = open(path, "rb")
            self = pickle.load(read_file) 
            self.client = oldClient
        except IOError:
            print('Error: File does not appear to exist.')
        with open(path, "rb") as read_file:
            self = pickle.load(read_file) 
            self.client = oldClient
    '''
    def archiveTradingData(self, asset_data_frame, stack_length = int): #TODO
        parent = os.getcwd() + "/ArchivedData/TradingData/" + self.name_of_data + "/{:%Y-%m/%d}/".format(datetime.datetime.today())
        child = self.name_of_data + '{:%H}'.format(datetime.datetime.today()) + "-trading-data.csv"
        child_localisation = "/" + child
                
        if not os.path.exists(parent):
            os.makedirs(parent)
        
        try:
            csv_file = open(parent + child_localisation, "a", newline='')
            data = [asset_data_frame.price, asset_data_frame.date, asset_data_frame.quantity, stack_length, self.wallet.quote_MG, self.wallet.base_MG]
            csv_writer = csv.writer(csv_file, delimiter = ',')
            csv_writer.writerow(data)
            csv_file.close()
        except Exception as error:
            print(error)
 
    def archiveTrasactionData(self, order, stack_length): #TODO TEST
        parent = os.getcwd() + "/ArchivedData/Transactions/" + self.name_of_data + "/{:%Y/%m/%d}/".format(datetime.datetime.today())
        child = "/" + self.name_of_data + '{:%d-%H}'.format(datetime.datetime.today()) + "-transactions.json"
        
        if not os.path.exists(parent):
            os.makedirs(parent)
        
        if not os.path.exists(parent+child):
            with open(parent+child, 'w', encoding='utf-8') as json_file:
                base_dictionary = {"transactions" : []}
                json.dump(base_dictionary, json_file)
        
        order["stack_length"] = stack_length
        data = {}
        with open(parent+child, 'r+', encoding='utf-8') as json_file:
            data = json.load(json_file)
        data['transactions'].append(order)
        
        with open(parent+child, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, indent = 4)
    
    def generateRaport(self):
        parent = os.getcwd() + "/ArchivedData/TradingData/" + self.name_of_data + "/Raports"
        child = '{:%Y-%m-%d-%H-%m-%S}'.format(datetime.datetime.today()) + "-raport.txt"
        child_localisation = "/" + child
        
        if not os.path.exists(parent):
            os.makedirs(parent)
        
        self.ending_time = datetime.datetime.now()
        
        raport = "successful_purchases: {}\nsuccessful_sells: {}\nwallet.quote_MG: {}\nwallet.base_MG: {}\nanalysed_data_frames: {}\nnew_exchange_rate: {}\nmin_wallet_price: {}\nmax_wallet_price: {}\nstarting_asset_price: {}\nending_asset_price: {}\nmin_asset_price: {}\nmax_asset_price: {}\nerror_amount: {}\nstarting_time: {}\nending_time: {}".format(
        self.successful_purchases,
        self.successful_sells,
        self.wallet.quote_MG,
        self.wallet.base_MG,
        self.analysed_data_frames,
        self.new_exchange_rate,
        self.min_wallet_price,
        self.max_wallet_price,
        self.starting_asset_price,
        self.new_exchange_rate,
        self.min_asset_price, 
        self.max_asset_price,
        self.error_amount,
        self.starting_time,
        self.ending_time)
        
        try:
            csv_file = open(parent + child_localisation, "w")
            csv_file.write(raport)
            csv_file.close()
        except Exception as error:
            print(error)
              
#Trading
    def transactionExecution(self, asset_data_frame, min_selling_value, min_profit_percentage, can_execute = bool):
        # Buying
        has_been_executed = False
        
        if (self.is_profitable_to_buy and can_execute):
            self.is_profitable_to_buy = False

            has_been_executed = self.buyAsset(asset_data_frame = asset_data_frame, amount = self.wallet.defaultOrderValue(self.new_exchange_rate))     
            # Measuring
            self.buyPrint(min_profit_percentage)
        # Selling
        if (self.is_profitable_to_sell and can_execute):
            self.is_profitable_to_sell = False
            
            has_been_executed = self.sellAsset(min_selling_value = min_selling_value, min_profit_percentage = min_profit_percentage)  
            # Measuring
            self.sellPrint(min_profit_percentage)

        return has_been_executed
    
    def innerBuyAsset(self, amount = None):
        if amount == None:
            amount = self.wallet.quote_MG*0.01/self.new_exchange_rate
        else:
            amount = float(amount)
        self.wallet.base_MG += amount
        self.wallet.quote_MG -= self.new_exchange_rate*amount

        return amount
    def innerSellAsset(self, assets, transactions_amount = int):
        assets = float(assets)
        self.wallet.base_MG -= assets
        self.wallet.quote_MG += assets*self.new_exchange_rate
        self.successful_sells += transactions_amount
        while transactions_amount > 0:
                self.exchange_rate_bought.pop()
                transactions_amount -= 1
    
    def order(self, side, quantity, symbol, order_type=ORDER_TYPE_MARKET): #TODO - TURN ON orders
        try:
            order_response = self.client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity) #TODO TEST ORDER - NOT VALID ORDER
        except Exception as e:
            print("Order exception occured => {}".format(e))
            self.error_amount += 1
            return False
        
        try:
            self.archiveTrasactionData(order_response, len(self.exchange_rate_bought))
        except Exception as e:
            print(e)

        return True
        
    def sellAsset(self, min_selling_value, min_profit_percentage = 0.007): #TODO
        # Analysis of amount of assets to sell
        testing_range = []
        for i in range(len(self.exchange_rate_bought)):
            testing_range.append(i)
        testing_range.reverse()

        memory = 0
        for i in testing_range:
            memory += 1
            #TODO Add current data
            if min_selling_value > self.exchange_rate_bought[i].price:
                break

        #Selling
        assets = decimal.Decimal('0.0')
        transactions_amount = memory
        while memory > 0:
            difference = self.new_exchange_rate - self.exchange_rate_bought[-memory].price 
            if (difference > 2*min_profit_percentage*self.exchange_rate_bought[-memory].price):
                self.exchange_rate_bought[-memory].printSellingData(Fore.BLACK, Back.GREEN, self.new_exchange_rate)    
            elif (difference > 0):
                self.exchange_rate_bought[-memory].printSellingData(Fore.WHITE, Back.BLUE, self.new_exchange_rate)
            else:
                self.exchange_rate_bought[-memory].printSellingData(Fore.BLACK, Back.YELLOW, self.new_exchange_rate)                   
            assets += decimal.Decimal(str(self.exchange_rate_bought[-memory].amount))
            memory -= 1

        has_been_executed = self.order(side = SIDE_SELL, quantity = assets, symbol = self.exchange_type)
        if has_been_executed:
            self.innerSellAsset(assets=assets, transactions_amount=transactions_amount)

        return has_been_executed
    
    def buyAsset(self, asset_data_frame, amount = decimal.Decimal):
        has_been_executed = self.order(side = SIDE_BUY, quantity = amount, symbol = self.exchange_type)
        
        if has_been_executed:
            probably_assets = self.innerBuyAsset(amount=amount)
            self.exchange_rate_bought.append(dc.DiffereceDataFrame(asset_data_frame, None, None, None, probably_assets, None, None))    
            self.successful_purchases += 1
         
        return has_been_executed      

#Printing
    def printWalletPrice(self):
        wallet_price = self.wallet.quote_MG + self.wallet.base_MG*self.new_exchange_rate
        print(Fore.WHITE + Back.MAGENTA + "Quote MG: {:2.5f}{} | Base MG: {:2.10f}{} | Current WP = {:2.5f}{}".format(self.wallet.quote_MG, self.wallet.quote_MG_type, self.wallet.base_MG, self.wallet.base_MG_type, wallet_price, self.wallet.quote_MG_type) + Style.RESET_ALL)   
    
    def printWalletTarget(self, target_value = float):
        base_MG_target = 0
        if len(self.exchange_rate_bought) > 0:        
            for trade in self.exchange_rate_bought:
                base_MG_target += trade.amount * trade.price * (1+target_value)
        wallet_price = self.wallet.quote_MG + base_MG_target
        print(Fore.WHITE + Back.MAGENTA + "Max WP: {:2.5f}{} | Min WP: {:2.5f}{} | Target WP = {:2.5f}{}".format(self.max_wallet_price, self.wallet.quote_MG_type, self.min_wallet_price, self.wallet.quote_MG_type, wallet_price, self.wallet.quote_MG_type) + Style.RESET_ALL)   

    def sellPrint(self, min_profit_percentage):
        print("All sells: " + str(self.successful_sells) + " => Current stack:" + str(len(self.exchange_rate_bought)))
        self.printWalletPrice()
        self.printWalletTarget(min_profit_percentage)
        
    def buyPrint(self, min_profit_percentage):
        print(Fore.WHITE + Back.RED + "Bought MG: {}{} => for:  {:7.2f}".format(self.exchange_rate_bought[-1].amount, self.wallet.base_MG_type, self.new_exchange_rate) + Style.RESET_ALL)
        if self.successful_purchases % 1 == 0:
            self.printWalletPrice()
            self.printWalletTarget(min_profit_percentage)
        
#Measurements
    def walletPriceAnalyser(self):
        wallet_price = self.wallet.quote_MG + self.wallet.base_MG*self.new_exchange_rate
        if wallet_price > self.max_wallet_price:
            self.max_wallet_price = wallet_price
        elif wallet_price < self.min_wallet_price:
            self.min_wallet_price = wallet_price
    
    def minMaxMGPrice(self):
        if self.analysed_data_frames == 1:
            self.starting_asset_price = self.new_exchange_rate
        if self.min_asset_price > self.new_exchange_rate:
            self.min_asset_price = self.new_exchange_rate
        if self.max_asset_price < self.new_exchange_rate:
            self.max_asset_price = self.new_exchange_rate

#Analysis Algorithms 
    def baseAlgorithm(self, asset_data_frame, min_profit_percentage = 0.006, min_loss_percentage = 0.0001, can_execute = True):
        has_been_executed = False
            
        if self.analysed_data_frames % 10000 == 0:
            self.printWalletPrice()
            self.printWalletTarget(min_profit_percentage)
            print(Fore.BLACK + Back.CYAN + "I have analysed {} trades!".format(self.analysed_data_frames) + Style.RESET_ALL)
        self.analysed_data_frames += 1
        self.new_exchange_rate = asset_data_frame.price
        
        #Measuring
        self.minMaxMGPrice()
        
        #Creating list of numbers to analyze
        self.exchange_rate.insert(0, self.new_exchange_rate)
        if len(self.exchange_rate) > len(self.bluring_kernel.kernel):
            self.exchange_rate.pop()
            
            #Bluring original data
            self.exchange_rate_2 = self.exchange_rate_1
            self.exchange_rate_1 = vfa.shortAnalysisWithBluringKernel(self.bluring_kernel, self.exchange_rate)

            #Creating diference in monotonicity
            self.delta_2 = self.delta_1
            self.delta_1 = self.exchange_rate_1 - self.exchange_rate_2
            
            # Analysis of change in monotonicity
            if (self.delta_1 > 0 and self.delta_2 < 0):
                self.is_changed_to_rising = True
            elif (self.delta_1 < 0 and self.delta_2 > 0):
                self.is_changed_to_decreasing = True
            
            # Analysis of buying profitability
            if (self.is_changed_to_rising and (len(self.exchange_rate_bought) == 0 or 
                    (self.exchange_rate_bought[-1].price - self.new_exchange_rate)/self.exchange_rate_bought[-1].price > min_loss_percentage)) and len(self.exchange_rate_bought) < self.wallet.max_amount_of_steps:
                self.is_profitable_to_buy = True
            
            # Analysis of selling profitability
            if len(self.exchange_rate_bought) > 0:
                self.min_selling_value = self.exchange_rate_bought[-1].price*(1+min_profit_percentage)
            if len(self.exchange_rate_bought) != 0 and self.new_exchange_rate > self.min_selling_value and self.is_changed_to_decreasing:
                self.is_profitable_to_sell = True
            
            #Transaction handling
            # Buying
            try:
                has_been_executed = self.transactionExecution(asset_data_frame, self.min_selling_value, min_profit_percentage, can_execute)
            except Exception as e:
                print(e)        
            #Measuring
            self.walletPriceAnalyser()    
            
            #Archive Data Frame
            self.archiveTradingData(asset_data_frame, len(self.exchange_rate_bought))
            
            self.is_changed_to_rising = False
            self.is_changed_to_decreasing = False   
            
        return has_been_executed

    def suddenDropAlorithm(self): #TODO
        pass
    
    def suddenRiseAlorithm(self): #TODO
        pass

 
