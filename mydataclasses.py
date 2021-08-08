from colorama import Fore, Back, Style
import os, pickle, json, math, decimal

class BluringKernel:
    def __init__(self, kernel = [], weight = 0):
        self.kernel = kernel
        self.weight = weight
        
class DataFrame:
    def __init__(self, symbol = str, price = float, date = int, quantity = float):
        self.symbol = symbol
        self.price = price
        self.date = date
        self.quantity = quantity
        
    def writeData(self, symbol = str, price = float, date = int, quantity = float):
        self.symbol = symbol
        self.price = price
        self.date = date
        self.quantity = quantity

    
    def printData(self, foreground, background, new_exchange_rate = float):
        difference = new_exchange_rate - self.price
        profit = difference * 100 / self.price
        print(foreground + background + "Sold asset:{:7.2f} => for:{:7.2f} => Differecne:{:7.2f} => Profit:{:2.4f}%".format(self.price, new_exchange_rate, difference, profit) + Style.RESET_ALL)   

class DiffereceDataFrame:
    def __init__(self, data_frame = None, symbol = str, price = float, date = int, amount = float, price_sold = float, date_sold = int):
        if data_frame != None:    
            self.symbol = data_frame.symbol
            self.price = data_frame.price
            self.date = data_frame.date 
        else:
            self.symbol = symbol
            self.price = price
            self.date = date 
        self.amount = amount
        self.price_sold = price_sold
        self.date_sold = date_sold
        
    def printSellingData(self, foreground, background, new_exchange_rate = float):
        difference = new_exchange_rate - self.price
        profit = difference * 100 / self.price
        print(foreground + background + "Sold asset:{} => for:{:7.10f} => Differecne:{:7.10f} => Profit:{:2.10f}%".format(self.amount, new_exchange_rate, difference, profit) + Style.RESET_ALL)
    
    def printBoughtData(self, foreground, background, new_exchange_rate = float):
        print(foreground + background + "Bought asset:{:7.10f} => for:{:7.10f}".format(self.amount, self.price) + Style.RESET_ALL)
        
class StackLenght:
    def __init__(self):
        self.length_of_selling_stack = []
        self.amount_of_sells = []      
 
 
    
class Wallet:
    def __init__(self, base_MG_type = str, base_MG = 0.0, base_MG_precision = float, quote_MG_type = str, quote_MG = 0.0, min_order_value = 10.5, price_precision = float, max_amount_of_steps = 0):
        #Base material goods info
        self.base_MG_type = base_MG_type
        self.base_MG = base_MG
        self.base_MG_precision = base_MG_precision
        #Quote material goods info
        self.quote_MG_type = quote_MG_type
        self.quote_MG = quote_MG
        self.min_order_value = min_order_value       
        #Exchange information
        self.price_precision = price_precision
        self.max_amount_of_steps = max_amount_of_steps
    
    def round_to_precision(self, number, precision: float = 1, which: str = ''):
        return decimal.Decimal(str(number)).quantize(decimal.Decimal(str(precision)), rounding=decimal.ROUND_UP) 
    
    def defaultOrderValue(self, current_exchange_rate):
        return self.round_to_precision(self.min_order_value / current_exchange_rate, self.base_MG_precision, 'up')
       
    def __dict__(self):
        return {"base_MG": self.base_MG, 'quote_MG': self.quote_MG, 'max_amount_of_steps': self.max_amount_of_steps, 'min_order_value': self.min_order_value, 'base_MG_type': self.base_MG_type, 'quote_MG_type': self.quote_MG_type}
 
        
class Waiter:
    def __init__(self):
        self.can_do = True
        
class Counter:
    def __init__(self):
        self.how_much = 0
    
class StackLenghtTest:
    def __init__(self, min_loss_percentage = float, min_profit_percentage = float):
        self.min_loss_percentage = min_loss_percentage
        self. min_profit_percentage = min_profit_percentage
        
class TradingInformation:
    def __init__(self):
        self.MG_info = self.load_MG_info()
    
    def load_MG_info(self, message = None):
        parent = os.getcwd() + "/WorkingData/SoftwareData"
        child = "/MG_info_data_file.pkl"    
        if not os.path.exists(parent):
            os.makedirs(parent)

        try:
            read_file = open(parent + child, "rb")
            MG_info = pickle.load(read_file)
            read_file.close()
            return MG_info
        except IOError as e:
            print(e)
            return None
    
    def save_exchange_info(self, message = dict):
        parent = os.getcwd() + "/WorkingData/SoftwareData"
        child = "/MG_info_data_file.pkl"    
        if not os.path.exists(parent):
            os.makedirs(parent)
        
        try:
            write_file = open(parent + child, "wb")
            pickle.dump(message, write_file)
            write_file.close()
            print("Trading information has been successfuly pickled.")
            return True
        except IOError:
            print('Error: File can not be opened.')
            return False
    
    def load_min_order_value(self, quote_MG_type = str):
        if quote_MG_type == 'XRP' or 'USDT' or 'TUSD' or 'BUSD' or 'USDC' or 'EUR' or 'GBP' or 'AUD' or 'BRL' or 'TRY' or 'PAX' or 'DAI' or 'VAI':
            min_order_value = 10
        elif quote_MG_type == 'RUB' or 'ZAR' or 'UAH' or 'TRX':
            min_order_value = 100
        elif quote_MG_type == 'BIDR' or 'IDRT':
            min_order_value = 20000
        elif quote_MG_type == 'NGN':
            min_order_value = 500
        elif quote_MG_type == 'BVND':
            min_order_value = 0.005
        elif quote_MG_type == 'ETH':
            min_order_value = 30000
        elif quote_MG_type == 'BTC':
            min_order_value = 0.0001
        elif quote_MG_type == 'BNB':
            min_order_value = 0.05
        else:
            return None
            
        return min_order_value
    
    def load_exchange_info(self):
        return self.MG_info['symbols']
        