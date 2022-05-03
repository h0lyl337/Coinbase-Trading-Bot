
from os import EX_CANTCREAT, remove
import cbpro
import subprocess
import time
import json
import threading
from datetime import datetime
import sqlite3
import sys, os

print('starting bot')
print('15 seconds to abort!')

### enable/disable simulation mode, buys sells with fake money for observation and testing purposes ###
SIMULATION_IO = True

### Allow the bot to automatically trade any coins for you based on your budget range ofcourse ###
AUTO_TRADE_MARKETS = False

### Allow autobuying of crypto ###
AUTO_BUY = True
### Amount of cryptos to work with at anytime ###
AUTO_BUY_COIN_TYPES = 5

#add the crypto you wanna watch to this list
crypto_list = ['ETH', 'BTC', 'ETC', 'DOGE', 'ADA']

CRYPTO_LIST_AUTO = ['BTC']
GOODLIST = []
coins_at_work = []
ranking = []


api_key = '< PUT HERE >'
secrete_key = '< PUT HERE >'

auth_client = cbpro.AuthenticatedClient(api_key, secrete_key, '< api password here >', api_url="https://api-public.sandbox.pro.coinbase.com")
public_client = cbpro.PublicClient()
account = auth_client.get_account('?????')
balance = auth_client.get_accounts()

### What currency to use to buy and sell crypto ###
CAPITAL_TYPE = 'USD'
CAPITAL_BALANACE = float()

### Range of capital you have to spend on trading ###
CAPITAL_RANGE_MIN = 100
CAPITAL_RANGE_MAX = 100

### PROFIT MODES how you would like to d ###
SPECIFIC_PROFIT_IO = False
PERCENTAGE_PROFIT_IO = True

SPECIFIC_PROFIT = 50
PERCENTAGE_PROFIT = 0.02

#STOP TRADING COIN IF BELOW PERCENTAGE OF 24HR LOW ###
DROP_IF_BELOW = 0.02

for ccc in public_client.get_currencies():
    #CRYPTO_LIST_AUTO.append(ccc['id'])
    print('turn on later 2345')

##change to initiate name ###
#get the price of all coins in crypto list.
def get_price():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    if AUTO_BUY == True:
        calibrate_auto_buy()
    else:
        for crypto in crypto_list:
            price = public_client.get_product_24hr_stats('{0}'.format(crypto + '-USD'))['last']
            for wallet in auth_client.get_accounts():
                if wallet['currency'] == crypto:
                    x = threading.Thread(target=start_bot, args=(crypto, wallet))
                    x.start()

### calibrate auto_buy ###
def calibrate_auto_buy():
### GEt capital balance ###
    for l in auth_client.get_accounts():
        if l['currency'] == CAPITAL_TYPE:
            CAPITAL_BALANCE = float(l['balance'])
            print('{0} capital : {1} '.format(l['currency'], CAPITAL_BALANCE))
            time.sleep(1)

    for crypto in CRYPTO_LIST_AUTO:
            if crypto in coins_at_work:
                pass
            time.sleep(2)
            try:
                CURRENT_PRICE = float(public_client.get_product_24hr_stats('{0}'.format(crypto + '-{0}'.format(CAPITAL_TYPE)))['last'])
                LOW_PRICE = float(public_client.get_product_24hr_stats('{0}'.format(crypto + '-{0}'.format(CAPITAL_TYPE)))['low'])
                HIGH_PRICE = float(public_client.get_product_24hr_stats('{0}'.format(crypto + '-{0}'.format(CAPITAL_TYPE)))['high'])

                ppprice = float(HIGH_PRICE - HIGH_PRICE*float(0.03))
                print(ppprice -float(CURRENT_PRICE))
                if ppprice - float(CURRENT_PRICE) >= float(CURRENT_PRICE)*float(0.03):
                    print('{0} good 24hr investiment'.format(crypto))
                    if crypto not in GOODLIST:
                        #GOODLIST.append(crypto)
                        ranking.append((crypto, ppprice -float(CURRENT_PRICE) ))
                        print(ranking)
                        print(87)            
                try:
                    if db_check_if_exist(crypto) == crypto:
                        print('{0} will continue where left off'.format(crypto))
                        if db_get_if_sold(crypto) == 0:
                            if crypto not in GOODLIST:
                                GOODLIST.append(crypto)
                            else:
                                pass
                        else:
                            print('removing {0} from database, already sold'.format(crypto))
                            info = db_get_coin_info(crypto)
                            bought = info[1]
                            amount = info[2]
                            sold = info[3]           
                            db_insert_sold(crypto, bought, amount, sold)   
                            db_remove_coin(crypto)
                            pass
                    else:
                        pass
                        
                except Exception as e:
                    print(99)
                    if str(e) == "'NoneType' object is not subscriptable":
                        print(55)
                        pass
            
            except Exception as e:
                if str(e) == "KeyError: 'last'":
                    print(123123)
                print(e)
        
    print(GOODLIST)
    rank_findings(GOODLIST)
    what_to_buy(GOODLIST)

### Deside on what to buy AUTO ###
def what_to_buy(list):
    print('----------------------------------------')
    print('checking what to buy')
    for crypto in list:
        print(crypto)           
        if db_check_if_exist(crypto) == crypto:
            print('{0} already purchased'.format(crypto))
            for wallet in auth_client.get_accounts():
                if wallet['currency'] == crypto:
                    x = threading.Thread(target=start_bot, args=(crypto, db_get_coin_info(crypto)[2], db_get_coin_info(crypto)[3], db_get_coin_info(crypto)[1]))
                    x.start()
        else:
            if SIMULATION_IO == True:
                print('simulating buy')
                db_insert_purchase(crypto, 0.214, 100, 103, 0) 
                print('bought {0}'.format(crypto))
                for wallet in auth_client.get_accounts():
                    if wallet['currency'] == crypto:
                        BOUGHT_PRICE = db_get_bought_price(crypto)
                        x = threading.Thread(target=start_bot, args=(crypto,100, 103, balance))
                        x.start()
            
            else:
                print('real sell disabled')                    
                #order = buy_waitfororder(crypto, 100)
                #balance = float(order[0])
                #done_reason = order[1]
                #status = order[2]
                #funds_spent = float(order[3])
                #target_sell_price = float(funds_spent) + float(funds_spent)*0.03
                #if status == 'done':
                    #if done_reason == 'filled':
                        #db_insert_purchase(crypto, balance, funds_spent, target_sell_price, 0) 
                        #print('bought {0}'.format(crypto))
                        #for wallet in auth_client.get_accounts():
                            #if wallet['currency'] == crypto:
                                #BOUGHT_PRICE = db_get_bought_price(crypto)
                                #x = threading.Thread(target=start_bot, args=(crypto,funds_spent, target_sell_price, balance))
                                #x.start()

    db_get_full_profits()         

#comepare the current price of the crypto to your desired price, just copy and paste an if function and change coin and price.
def check_crypto(crypto, price):
    if crypto == 'ETH-USD':
        if float(price) >=3000:
       
            notify('Etherium is at {0}'.format(price))

### Set how much you paid for the coin ###
def get_coin_bought_price(coin):
    if coin == 'ETH':
        BOUGHT_PRICE = 3500.00
    
    if coin == 'BTC':
        BOUGHT_PRICE = 35000.00

    if coin == 'ETC':
        BOUGHT_PRICE = 3500.00

    if coin == 'DOGE':
        BOUGHT_PRICE = 3500.00

    if coin == 'ADA':
        BOUGHT_PRICE = 200.00
    
    return BOUGHT_PRICE
            
def start_bot(crypto, FUNDS_SPENT, TARGET_PRICE, COIN_BALANCE):

        if crypto in coins_at_work:
            print('{0} is already running. will pass'.format(crypto))
            pass
        else:
            price = public_client.get_product_24hr_stats('{0}'.format(crypto + '-{0}'.format(CAPITAL_TYPE)))['last']
            print(price)
            print('Balance : {0} {1}'.format(COIN_BALANCE, crypto))
            coins_at_work.append(crypto)
            while 1:
                time.sleep(5)
                price = public_client.get_product_24hr_stats('{0}'.format(crypto + '-{0}'.format(CAPITAL_TYPE)))['last']
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")

                if AUTO_BUY == True:
                    coin_bought_price = db_get_bought_price(crypto)

                else:
                    coin_bought_price = get_coin_bought_price(crypto)

                PROFIT = float(price) * float(COIN_BALANCE)
                print('{0} bought {1} '.format(crypto, coin_bought_price))
                print('{0} current '.format(crypto) + public_client.get_product_24hr_stats('{0}'.format(crypto + '-{0}'.format(CAPITAL_TYPE)))['last'])
                print('{0} Low '.format(crypto) + public_client.get_product_24hr_stats('{0}'.format(crypto + '-{0}'.format(CAPITAL_TYPE)))['low'])
                print('{0} high '.format(crypto) + public_client.get_product_24hr_stats('{0}'.format(crypto + '-{0}'.format(CAPITAL_TYPE)))['high'])


                ### if the current coin price is equal or greathan than the 24hr low ###
                if float(price) <= float(coin_bought_price)-float(coin_bought_price)*float(0.01):
                    print('dropping out')
                    ######ADDDD add loss to database
                    db_insert_sold(crypto, FUNDS_SPENT, COIN_BALANCE, FUNDS_SPENT)
                    db_remove_coin(crypto)
                    exit()

                ### if profit is greater than or equal to limit sell and exit ###
                
                if SPECIFIC_PROFIT_IO == True:
                    if PROFIT > SPECIFIC_PROFIT:
                        print('We did it boiii')
                        print('selling {0}'.format(crypto))
                        db_mark_sold(crypto)
                        db_insert_sold(crypto, FUNDS_SPENT, COIN_BALANCE, FUNDS_SPENT*float(0.02)+FUNDS_SPENT)
                        db_remove_coin(crypto)
                        exit()
                
                if PERCENTAGE_PROFIT_IO == True:
                    print(2222222)
                    coin_target_price = db_get_coin_info(crypto)[3]
                    print(coin_target_price)
                    print(COIN_BALANCE)
                    if float(price)*float(COIN_BALANCE) >= float(coin_target_price) :
                        print('We did it boiiizzzzzzzzzzzzzzzzzzz')
                        print('selling {0}'.format(crypto))
                        if SIMULATION_IO == True:
                            print('simulating sell')

                            db_mark_sold(crypto)
                            db_insert_sold(crypto, FUNDS_SPENT, COIN_BALANCE, FUNDS_SPENT*float(0.03)+FUNDS_SPENT)
                            db_remove_coin(crypto)
                            exit()
                        
                        else:
                            #sell_waitfororder(crypto, COIN_BALANCE, TARGET_PRICE)
                            db_mark_sold(crypto)
                            db_insert_sold(crypto, FUNDS_SPENT, COIN_BALANCE, FUNDS_SPENT*float(0.03)+FUNDS_SPENT)
                            db_remove_coin(crypto)
                            exit()

def rank_findings(ranking):
    print('ranking bby ranking')
    for items in GOODLIST:
        print(items)
        print(ranking)



def buy_waitfororder(crypto, purchase_amount):
    print(crypto, purchase_amount)
    print('buying order')
    e = auth_client.place_market_order(product_id='{0}-{1}'.format(crypto, CAPITAL_TYPE), 
                               side='buy', 
                               funds='{0}'.format(purchase_amount))


    order = auth_client.get_order(e['id'])
    done_reason = order['done_reason']
    amount = order['filled_size']
    status = order['status']
    funds_spent = order['specified_funds']

    print(order)
    print(amount)
    print(done_reason)
    print(status)
    print(funds_spent)

    return amount, done_reason, status, funds_spent


def sell_waitfororder(crypto, coin_balance, target_amount):
    print('selling order')
    e = auth_client.sell(price='{0}'.format(target_amount), #USD
                size='{0}'.format(coin_balance), #BTC
                order_type='limit',
                product_id='{0}-{1}'.format(crypto, CAPITAL_TYPE))


    order = auth_client.get_order(e['id'])
    done_reason = order['done_reason']
    amount = order['filled_size']
    status = order['status']


    print(order)
    print(amount)
    print(done_reason)
    print(status)


    return amount, done_reason, status

def distribute_funds():
    print('how to distrubute funds')
    for crypto in ranking:
        print(crypto)



#notify for kde when your price is hit or lower.
def notify(message):
    subprocess.call(["notify-send", "{0}".format(message)])


def mainloop():
    subprocess.call(["notify-send", "Starting Crypto checker!"]) 
    get_price()

def loop_scanning():
        get_price()

###########################################################################################################################

def create_database():
    print('creating database')
    con = sqlite3.connect('1337bot')
    c = con.cursor()

    c.execute('''
          CREATE TABLE IF NOT EXISTS purchases
          (coin varchar(32), balance int(32), purchased_price int(32), target_sell_price int(32), sold int(2));''')
    db_create_banned_table()
    db_create_sold_table()

def db_check_if_exist(coin):
    try:
        con = sqlite3.connect('1337bot')
        c = con.cursor()

        c.execute('SELECT coin FROM purchases WHERE coin= "{0}" '.format(coin))
    
        return c.fetchone()[0]

    except Exception as e:
        if str(e) == "'NoneType' object is not subscriptable":
            return 'None'


def db_get_bought_price(coin):
        con = sqlite3.connect('1337bot')
        c = con.cursor()
        try:
            c.execute('SELECT purchased_price FROM purchases WHERE coin="{0}" '.format(coin))
            return c.fetchone()[0]
        except Exception as e:
            if str(e) == "TypeError: 'NoneType' object is not subscriptable":
                return float(0.00)


    

def db_insert_purchase(coin, balance, purchased_price, target_sell_price, sold):
    print('inserting purchases to DB.')
    print(coin, balance, purchased_price, target_sell_price, sold)
    if balance == 'None':
        balance = float(0.00)
    con = sqlite3.connect('1337bot')
    c = con.cursor()
    try:
        c.execute(''' INSERT INTO purchases (coin,balance,purchased_price,target_sell_price,sold) VALUES ("{0}",{1},{2},{3},{4}) '''.format(coin, balance, purchased_price, target_sell_price, sold))
        con.commit()

    except Exception as e:
        print(e)
        pass



def db_get_if_sold(coin):
    con = sqlite3.connect('1337bot')
    c = con.cursor()

    c.execute('SELECT sold FROM purchases WHERE coin="{0}" '.format(coin))

    return c.fetchone()[0]

def db_get_coin_info(coin):
    con = sqlite3.connect('1337bot')
    c = con.cursor()

    c.execute('SELECT * FROM purchases WHERE coin="{0}" '.format(coin))

    return c.fetchone()


def db_get_coin_balance(coin):
    con = sqlite3.connect('1337bot')
    c = con.cursor()

    c.execute('SELECT target_sell_price FROM purchases WHERE coin="{0}" '.format(coin))

    return c.fetchone()[0]

def db_mark_sold(coin):
    con = sqlite3.connect('1337bot')
    c = con.cursor()

    c.execute('UPDATE purchases SET sold = 1 WHERE coin="{0}" '.format(coin))
    con.commit()


def db_remove_coin(coin):
    con = sqlite3.connect('1337bot')
    c = con.cursor()

    c.execute('DELETE FROM purchases WHERE coin = "{0}" '.format(coin))
    con.commit()

def db_ban_coin(coin):
    con = sqlite3.connect('1337bot')
    c = con.cursor()

    c.execute('INSERT INTO banned (coin,count) VALUES ("{0}",{1})'.format(coin, 1))
    con.commit()

def db_check_ban_coin(coin):
    con = sqlite3.connect('1337bot')
    c = con.cursor()
    c.execute('SELECT coin FROM banned WHERE coin = "{0}" '.format(coin))

    return c.fetchone[0]

def db_check_ban_coin_count(coin):
    con = sqlite3.connect('1337bot')
    c = con.cursor()
    c.execute('SELECT count FROM purchases WHERE coin = "{0}" '.format(coin))

    return c.fetchone[0]

def db_create_banned_table():
    con = sqlite3.connect('1337bot')
    c = con.cursor()

    c.execute('''
          CREATE TABLE IF NOT EXISTS banned
          (coin varchar(32), count int(32));''')


def db_create_sold_table():
    con = sqlite3.connect('1337bot')
    c = con.cursor()

    c.execute('''
          CREATE TABLE IF NOT EXISTS sold
          (coin varchar(32), bought int(32), amount int(32), sold int(32));''')


def db_insert_sold(coin, bought, amount, sold):
    con = sqlite3.connect('1337bot')
    c = con.cursor()

    c.execute('INSERT INTO sold (coin,bought,amount,sold) VALUES ("{0}",{1}, {2}, {3})'.format(coin, bought, amount, sold))
    con.commit()

def db_get_sold():
    con = sqlite3.connect('1337bot')
    c = con.cursor()

    c.execute('SELECT * FROM sold;')
    return c.fetchone[0]


def db_get_full_profits():
    con = sqlite3.connect('1337bot')
    c = con.cursor()
    c.execute('SELECT * FROM sold;')
    profit_list = []
    for coin in c.fetchall():
        crypto = coin[0]
        bought = coin[1]
        amount = coin[2]
        sold = coin[3]
        profit_list.append(sold*amount-bought*amount)
    p = float()

    for profit in profit_list:
        p = p+profit
    print('profits : {0}'.format(p))


create_database()
get_price()



