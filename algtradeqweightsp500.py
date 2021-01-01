# freecodecamp Algorithmic Trading - Equal-Weight S&P 500

import numpy as np # one or two dimensional arrays/tensors
import pandas as pd # spreadsheets, tabular
import requests # html
import xlsxwriter
import math

stocks = pd.read_csv('sp_500_stocks.csv')
type(stocks) # print? tells what type

# store in secrets.py files to keep it secret, doesn't get pushed to git
from secrets import IEX_CLOUD_API_TOKEN

symbol = 'AAPL'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote/?token={IEX_CLOUD_API_TOKEN}' #f {} uses variable, symbol in the first case. stable for stable API version.
data = requests.get(api_url).json() # use .json() for dictionary
print(data)

price = data['latestPrice']
market_cap = data['marketCap']
print(market_cap)

my_column = ['Ticker', 'Stock Price', 'Market Capitalization', 'Number of Shares to Buy']
final_dataframe = pd.DataFrame([[0, 0, 0, 0]], columns = my_columns)
final_dataframe

final_dataframe.append(pd.Series([symbol, price, market_cap], index = my_columns), ignore_index = True)

final_dataframe = pd.DataFrame(columns = my_columns)
for stock in stocks['Ticker']:
    api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote/?token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(api_url).json()
    final_dataframe = final_dataframe.append(pd.Series([stock, data['latestPrice'], data['marketCap']], index = my_columns), ignore_index = True)

final_dataframe

# Use Batch API Calls to Improve Performance :)
def chunks(list, n):
    # Yield successive n-sized chunks from list.
    for i in range(0, len(list), n):
        yield list[i:i + n]

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
    # print(symbol_groups[i])

final_dataframe = pd.DataFrame(columns = my_columns)
for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_uri).json()
    for symbol in symbol_string.split(','):
        print(symbol)
        final_dataframe = final_dataframe.append(pd.Series([symbol, data[symbol]['quote']['latestPrice'], data[symbol]['quote']['marketCap']], index = my_columns), ignore = True)

final_dataframe

# Calculating the Number of Shares to Buy
while True:
    try:
        porfolio_size = int(input('Enter the dollar amount (exclude change): $'))
        break
    except:
        print('Error: Enter an integer.')
val = float(porfolio_size)

position_sze = val/len(final_dataframe.index)
number_of_apple_shares = position_size/500
print(math.floor(number_of_apple_shares))

for i in range(0, len(final_dataframe.index)):
    final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size/final_dataframe.loc[i, 'Stok Price'])

final_dataframe

# Formatting Our Excel Ouput
writer = pd.ExcelWriter('recommended trades.xlsx', engine = 'xlsxwriter')
final_dataframe.to_excel(writer, 'Recommended Trades', index = False)

# Creating the formats we'll need for our .xlsx file
    # colors
background_color = '#0a0a23'
font_color = '#ffffff'
string_format = writer.book.add_format({'font_color': font_color, 'bg_color' : background_color, 'border' : 1})
dollar_format = writer.book.add_format({'num_format': '$0.00', 'font_color': font_color, 'bg_color' : background_color, 'border' : 1})
integer_format = writer.book.add_format({'num_format': '0', 'font_color': font_color, 'bg_color' : background_color, 'border' : 1})

# the for loop does these two groups in two lines
'''
writer.sheets['Recommended Trades'].set_column('A:A', 18, string_format)
writer.sheets['Recommended Trades'].set_column('B:B', 18, string_format)
writer.sheets['Recommended Trades'].set_column('C:C', 18, string_format)
writer.sheets['Recommended Trades'].set_column('D:D', 18, string_format)
writer.save()

writer.sheets['Recommended Trades'].write('A1', 'Ticker', string_format)
writer.sheets['Recommended Trades'].write('B1', 'Stock Price', dollar_format)
writer.sheets['Recommended Trades'].write('C1', 'Market Capitalization', dollar_format)
writer.sheets['Recommended Trades'].write('D1', 'Number of Shares to Buy', integer_format)
'''
column_formats = {'A': ['Ticker', string_format], 'B': ['Stock Price', dollar_format], 'C': ['Market Capitalization', dollar_format], 'D': ['Number of Shares to Buy', integer_format]}

for column in column_formats.keys():
    writer.sheets['Recommended Trades'].set_column(f'{column}:{column}', 18, column_formats[column][1])
    writer.sheets['Recommended Trades'].write(f'{column}1', column_formats[column][0], column_formats[column][1])

writer.save()
