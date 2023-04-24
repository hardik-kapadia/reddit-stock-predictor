from get_stocks import get_stock,get_stock_from_symbol
from scores import get_score

stock = get_stock_from_symbol("TSLA","Tesla",["car"])
print(stock)

get_score(stock)