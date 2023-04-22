import models
import investpy
import yfinance as yf
import stockquotes

# from yahoo_fin import stock_info as si

def get_current_stock_price(symbol):
    try:
        _stock_ = stockquotes.Stock(symbol)
        price = _stock_.current_price
    except:
        return 0
    return float(price)


def get_stock(stockname):
    stocks = []
    try:
        search_results = investpy.search_quotes(
            text=stockname, products=['stocks'], n_results=10)
    except RuntimeError:
        print('no stocks found')
        return None
    
    for i in search_results:
        name = i.name
        symbol = i.symbol
        country = i.country
        yfstock = yf.Ticker(symbol)
        hist = yfstock.history(period='6d')
        
        _stock = models.stock(name, symbol, hist, country)
        stocks.append(_stock)
    return stocks

def get_stock_from_symbol(symbol,name,keywords: list = []):
    
    yfstock = yf.Ticker(symbol)
    hist = yfstock.history(period='6d')
    
    return models.Stock(name,symbol,hist, keywords)