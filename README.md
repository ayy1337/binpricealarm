# binpricealarm

Small little script that watches the prices on Binance's alt-btc pairs, and alerts when they've moved up some % in a given time (hour by default).

# Dependencies
You will need at a minimum the binance API module:
`pip install python-binance`

For sound alert:
`pip install playsound`


If you are on windows and want desktop notifications:
`pip install setuptools pypiwin32 win10toast` 


If on linux and want desktop notifications, you will need pygobject; http://pygobject.readthedocs.io/en/latest/getting_started.html#ubuntu-getting-started
