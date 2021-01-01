# freecodecamp A Quantitative Momentum Investing Strategy

import numpy as np # numerical computing
import pandas as pd # data science
import requests # for making http requests
import math
from scipy.stats import percentileofscore as score# instead of importing the entire scipy library, we just grab stats
import xlsxwriter

stocks = pd.read_csv('sp_500_stocks.csv')
from secrets import IEX_CLOUD_API_TOKEN

symbol = 'AAPL'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/stats/'
data = requests.get(api_url).json()

# Parsing Our API Call
#data[''] # put a specific thing in data (print it first and then put specific thing in string)

def chunks(list, n):
    # Yield successive n-sized chunks from list.
    for i in range(0, len(list), n):
        yield list[i:i + n]

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))

my_columns = ['Ticker', 'Price', 'One-Year Price Return', 'Number of Shares to Buy']

# create blank DataFrame
final_dataframe = pd.DataFrame(columns = my_columns)

for symbol_string in symbol_strings:
    batch_api_call_uri = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=price,statsquote,news,chart&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    print(data['AAPL']['stats'])
    for i in symbol_string.split(','):
        final_dataframe = final_dataframe.append(pd.Series([symbol, data[symbol]['price'], data[symbol]['stats'], ['year1ChangePercent'], 'N/A'], index = my_colums), ignore_index = True)

# Removing Low-Momentum Stocks
final_dataframe.sort_values('One-Year Price Return', ascending = False, inplace = True)
final_dataframe = final_dataframe[:50]

def portfolio_size():
    global portfolio_size
    portfolio_size = input('Enter the size of your portfoloio:')

    try:
        float(portfolio_size)
    except:
        print('That is not a number! \nPlease try again:')
        portfolio_size = input('Enter the size of your portfolio:')

portfolio_input()
position_size = float(portfolio_size)/len(final_dataframe.index)

# Building a Better (and More Realistc) Momentum Strategy
hqm_column = ['Ticker', 'Price', 'Number of Shares to Buy', 'One-Year Price Return', 'One-Year Return Percentile', 'Six-Month Price Return', 'Six-Month Return Percentile', 'Three-Month Price Return', 'Three-Month Return Percentile', 'One-Month Price Return', 'One-Month Return Percentile']

hqm_dataframe = pd.DataFrame(columns = hqm_columns)
for symbol_string in symbol_strings:
    batch_api_call_uri = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=price,statsquote,news,chart&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        hqm_dataframe = hqm_dataframe.append(pd.Series[symbol, data[symbol]['Price'], 'N/A', data[symbol]['stats']['year1ChangePercent'], 'N/A', data[symbol]['stats']['month6ChangePercent'], 'N/A', data[symbol]['stats']['month3ChangePercent'], 'N/A'], index = hqm_columns), ignore_index = True)

time_periods = ['One-Year', 'Six-Month', 'Three-Month', 'One-Month']

for row in hqm_dataframe.index:
    for time_period in time_periods:
        change_col = f'{time_period} Price Percentile'
        percentile_col = f'{time_period} Return Percentile'
        hqm_dataframe.loc[row, percentile_col] = score(hqm_dataframe[change_col], hqm_dataframe.loc[row, f'{time_period} Return Percentile'])

hqm_dataframe

# Calculating the HQM Score
from statistics import mean

for row in hqm_dataframe.index[:1]:
    momentum_percentiles = []
    for time_period in time_periods:
        momentum_percentiles.append(hqm_dataframe.loc[row, f'{time_period} Return'])
    hqm_dataframe.loc[row, 'HQM Score'] = mean(momentum_percentiles)

hqm_dataframe

# Selecting the 50 Best Momentum Stocks
hqm_dataframe.sort_values('HQM Score', ascending = False, inplace = True)
hqm_dataframe = hqm_dataframe[:50]
hqm_dataframe.reset_index(inplace = True, drop = True)

# Calculating the Number of Shares to Buy
portfolio_input()

position_size = float(portfolio_size)/len(hqm_dataframe.index)
for i in hqm_dataframe.index:
    hqm_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size/hqm_dataframe.loc[i, 'Price'])

hqm_dataframe

# Formatting Our Excel Output
writer = pd.ExcelWriter('momentum_strategy.xlsx', engine = 'xlsxwriter')
hqm_dataframe.to_excel(writer, sheet_name = "Momentum Strategy", index = False)

# Creating the Formats We'll Need For Our
background_color = '#0a0a23'
font_color = '#ffffff'
string_format = writer.book.add_format({'font_color': font_color, 'bg_color' : background_color, 'border' : 1})
dollar_format = writer.book.add_format({'num_format': '$0.00', 'font_color': font_color, 'bg_color' : background_color, 'border' : 1})
integer_format = writer.book.add_format({'num_format': '0', 'font_color': font_color, 'bg_color' : background_color, 'border' : 1})


column_formats = {'A': ['Ticker', string_template], 'B': ['Price', dollar_template], 'C': ['Number of Shares to Buy', integer_template], 'D': ['One-Year Price Return', percent_template], 'E': ['One-Year Return Percentile', percent_template], 'F': ['Six-Month Price Return', percent_template], 'G': ['Six-Month Return Percentile', percent_template], 'H': ['Three-Month Price Return', percent_template], 'I': ['Three-Month Return Percentile', percent_template], 'J': ['One-Month Price Return', percent_template], 'K': ['One-Month Return Percentile', percent_template] 'L': ['HQM Score', percent_template]}

for column in column_formates.keys():
    writer.sheets['Momentum Strategy'].set_column(f'{column}:{column}', 22, column_formats[column])
    writer.sheets['Momentum Strategy'].write(f'{column}1', column_formats[column][0], column_formats[column][1])


# Saving Our Excel Output
writer.save()
