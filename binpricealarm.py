from binance.client import Client

import time, sys, os

candle_interval = 60*5 #5 mins

numcandles = 12 #1hr

targetchange = 1.1 #1.1 = 10% increase

notifywait = 6*60*60 #amount of time in seconds to wait before alerting again on same coin; default 6 hrs

lastnotified = {}
tonotify = []


candles = []
#each candle is 5mins

api = Client("","")
notification_support = 0
sound_support = 0
if os.name == "NT":
    platform = "win"
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        notification_support = 1
    except:
        pass
else:
    platform = "lin"
    try:
        from gi.repository import Notify
        Notify.init("BinancePriceAlert")
        notification_support = 1
    except:
        pass

try:
    from playsound import playsound
    #you can replace Alarm.wav with whatever .wav file you want, though playsound is blocking so prolly use a short one..
    if platform == "win":
        soundpath = os.getcwd() + "\\Sound\\Alarm.wav"
    elif platform == "lin":
        soundpath = os.getcwd() + "/Sound/Alarm.wav"
    sound_support = 1
except:
    pass



def notify():
    global tonotify
    if platform == "win":
        if notification_support and toaster.notification_active():
            return
    
    coins = tuple([d.split("BTC")[0] for d in tonotify])
    timestamp = time.strftime("%Y-%m-%d %H:%M")
    msg = ", ".join(coins) + " moving up!"
    print("{}: {}".format(timestamp, msg))

    try:
        if notification_support:
            if platform == "win":
                toaster.show_toast("Binance Alert!",
                           msg,
                           icon_path=None,
                           duration=10,
                           threaded=True)
                curtime = time.time()
            elif platform == "lin":
                Notify.Notification.new("Binance Alert", msg).show()
        if sound_support:
            playsound(soundpath)
        for coin in tonotify:
            lastnotified[coin] = curtime
        tonotify = []
    except Exception:
        pass
    return

def getprices():
    try:
        r = api.get_all_tickers()
        prices = {}
        for item in r:
            symbol = item['symbol']
            if symbol.endswith("BTC"):
                prices[symbol] = float(item['price'])
        return prices
    except Exception:
        return -1

def mknewcandle(prices):
    currtime = int(time.time())
    timestamp = currtime - currtime%candle_interval
    coins = {}
    for i in prices:
        p = prices[i]
        coins[i] = [p,p,p,p] #this is [open, high, low, close]
    return [timestamp,coins]

def updatecandles():
    global candles
    prices = getprices()

    if prices == -1:
        return

    for i in range(len(candles)):
        if candles[0][0] < (candles[-1][0] - ((numcandles+1) * candle_interval)): #get rid of old candle data
            candles = candles[1:]
        else:
            break

    if (len(candles) == 0) or ((len(candles) > 0) and ((time.time() - candles[-1][0]) > candle_interval)): #check if new candle needs be made
        candles.append(mknewcandle(prices))
        if len(candles) > numcandles:
            candles = candles[1:]

    else:
        currcandle = candles[-1]
        for i in prices:
            
            p = prices[i]
            try:
                c = currcandle[1][i] #coin's ohlc array in currcandle
                if p > c[1]:
                    c[1] = p
                if p < c[2]:
                    c[2] = p
                c[3] = p
            except:
                c = [p,p,p,p]
                currcandle[1][i] = c

def checkchange():
    global tonotify
    global candles

    if len(candles) > 0:
        currcandle = candles[-1]
        for i in currcandle[1]:
            if ((i in lastnotified) and ((time.time() - lastnotified[i]) > notifywait)) or (i not in lastnotified):
                c = currcandle[1][i]
                currprice = c[3]
                for candle in candles:
                    try:
                        if currprice > (targetchange * candle[1][i][2]):
                            
                            if i not in tonotify:
                                tonotify.append(i)
                            break

                    except Exception:
                        pass
    if len(tonotify) > 0:
        notify()


while 1:
    updatecandles()
    checkchange()
    time.sleep(2)
