# freecodecamp Quantitative Value Investing Strategy

# Library Imports
import numpy as np
import pandas as pd
import xlsxwriter
import requests
from scipy import stats
import math

# Importing Our List of Stocks  & API Token
stocks = pd.read_csv('sp_500_stocks.csv')
from secrets import IEX_CLOUD_API_TOKEN

# Making Our First API Call
symbol = 'aapl'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
data = requests.get(api_url).json()
print(data.status_code)
print(data)

# Parsing Our API Call
price = data['latestPrice']
pe_ratio = data['peRatio']

# Executing A Batch API Call & Building Our DataFrame
def chunks(list, n):
    # Yield successive n-sized chunks from list.
    for i in range(0, len(list), n):
        yield list[i:i + n]

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))

my_columns = ['Ticker', 'Price', 'Price-to-Earnings Ratio', 'Number of Shares to Buy']

final_dataframe = pd.DataFrame(columns = my_columns) # columns with column names

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(pdSeries([symbol, data[symbol]['quote']['latestPrice'], data[symbol]['quote']['peRatio'], 'N/A'], index = my_columns), ignore_index = True)

# Removing Glamour Stocks
final_dataframe.sort_values('Price-to-Earnings Ratio', ascending = True, inplace = True)
final_dataframe = final_dataframe[final_dataframe['Price-to-Earnings Ratio'] > 0]
final_dataframe = final_dataframe[:50]
final_dataframe.reset_index(inplace = True)
final_dataframe.drop('index', axis = 1, inplace = True)

# Calculating the Number of Shares to Buy
def portfolio_size():
    global portfolio_size
    portfolio_size = input('Enter the size of your portfoloio:')

    try:
        val = float(portfolio_size)
    except ValueError:
        print('That is not a number! \nPlease try again:')
        portfolio_size = input('Enter the size of your portfolio:')

position_size = float(portfolio_size)/len(final_dataframe.index)
for row in final_dataframe.index:
    final_dataframe.loc[row, 'Number of Shares to Buy'] = math.floor(position_size/final_dataframe.loc[row, 'Price'])

final_dataframe # or put in print statement??

# Building a Better(and More Realistic) Momentum Strategy
symbol = 'AAPL'
batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol}&types=quote&token={IEX_CLOUD_API_TOKEN}'
data = requests.get(batch_api_call_url).json()

pe_ratio = data[symbol]['quote']['peRatio'] # Price-to-earnings ratio
pb_ratio = data[symbol]['advanced-stats']['priceToBook'] # Price-to-book ratio
ps_ratio = data[symbol]['advanced-stats']['priceToSales'] # Price-to-sales ratio

enterprise_value = data[symbol]['advanced-stats']['enterpriseValue']
ebitda = data[symbol]['advanced-stats']['EBITDA']
ev_to_ebitda = enterprise_value/ebitda # Enterprise value divided by earnings before interest, taxes, deprecation, and amortization (EV/EBITDA)

gross_profit = data[symbol]['advanced-stats']['grossProfit']
ev_to_gross_profit = enterprise_value/gross_profit # Enterprise value divided by gross profit (EV/GP)

rv_columns = ['Ticker', 'Price', 'Number of Shares to Buy', 'Price-to-Earnings Ratio', 'PE Percentile', 'Price-to-Book Ratio', 'PB Percentile', 'Price-to-Sales Ratio', 'PS Percentile', 'EV/EBITDA', 'EV/EBITDA Percentile', 'EV/GP', 'EV/GP Percentile', 'RV Score']

rv_dataframe = pd.DataFrame(columns = rv_columns)

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        enterprise_value = data[symbol]['advanced-stats']['enterpriseValue']
        ebitda = data[symbol]['advanced-stats']['EBITDA']
        gross_profit = data[symbol]['advanced-stats']['grossProfit']

        try:
            ev_to_ebitda = enterprise_value/ebitda
        except TypeError:
            ev_to_ebitda = np.NaN
        try:
            ev_to_gross_profit = enterprise_value/gross_profit
        except TypeError:
            ev_to_gross_profit = np.NaN

        rv_dataframe = rv_dataframe.append(pd.Series([symbol, data[symbol]['quote']['latestPrice'], 'N/A', data[symbol]['quote']['peRatio'], 'N/A', data[symbol]['advanced-stats']['priceToBook'], 'N/A', data[symbol]['advanced-stats']['priceToSales'], 'N/A', ev_to_ebitda, 'N/A', enterprise_value/gross_profit, 'N/A', 'N/A'], index = rv_columns), ignore_index = True)

# Dealing with Missing Data in Our DataFrame

for column in ['Price-to-Earnings Ratio', 'Price-to-Book Ratio', 'Price-to-Sales Ratio', 'EV/EBITDA', 'EV/GP']:
    rv_dataframe[column].fillna(rv_dataframe[column].mean(), inplace = True)

rv_dataframe[rv_dataframe.usnull().any(axis=1)] # could use len(rv...)].index) to see how much is missing

rv_dataframe.columns

# Calculating Value Percentiles
from scipy.stats import percentileofscore as score

metrics = {'Price-to-Earnings Ratio': 'PE Percentile', 'Price-to-Book Ratio': 'PB Percentile', 'Price-to-Sales Ratio': 'PS Percentile', 'EV/EBITDA': 'EV/EBITDA Percentile', 'EV/GP': 'EV/GP Percentile'}
for metric in metrics.keys():
    for row in rv_dataframe.index:
        rv_dataframe.loc[row, metrics[metric]] = score(rv_dataframe[metric], rv_dataframe.loc[row, metric])

# Calculating the RV Score
from statistics import mean
for row in rv_dataframe.index:
    value_percentiles = []
    for metric in metrics.keys():
        value_percentiles.append(rv_dataframe.loc[row, metrics[metric]])
    rv_dataframe.loc[row, 'RV Score'] = mean(value_percentiles)

# Selecting the 50 Best Momentum Stocks
rv_dataframe.sort_values('RV Score', ascending = True, inplace = True)
rv_dataframe = rv_dataframe[:50]
rv_dataframe.reset_index(drop = True, inplace = True)

# Calculating the Number of Shares to Buy
portfolio_input()

position_size = float(portfolio_size)/len(rv_dataframe.index)
for row in rv_dataframe.index:
    rv_dataframe.loc[row, 'Number of Shares to Buy'] = math.floor(position_size/rv_dataframe.loc[row, 'Price'])

# Formatting Our Excel Output
writer = pd.ExcelWriter('value_strategy.xlsx', engine = 'xlsxwriter')
rv_dataframe.to_excel(writer, sheet_name = 'Value Strategy', index = False)

# Creating the Formats We'll Need For Our .xlsx File
background_color = '#0a0a23'
font_color = '#ffffff'
string_format = writer.book.add_format({'font_color': font_color, 'bg_color' : background_color, 'border' : 1})
dollar_format = writer.book.add_format({'num_format': '$0.00', 'font_color': font_color, 'bg_color' : background_color, 'border' : 1})
integer_format = writer.book.add_format({'num_format': '0', 'font_color': font_color, 'bg_color' : background_color, 'border' : 1})

column_formats = {'A': ['Ticker', string_template], 'B': ['Price', dollar_template], 'C': ['Number of Shares to Buy', integer_template], 'D': ['Price-to-Earnings Ratio', float_template], 'E': ['PE Percentile', percent_template], 'F': ['Price-to-Book Ratio', float_template], 'G': ['PB Percentile', percent_template], 'H': ['Price-to-Sales Ratio', float_template], 'I': ['PS Percentile', percent_template], 'J': ['EV/EBITDA', float_template], 'K': ['EV/EBITDA Percentile', percent_template], 'L': ['EV/GP', float_template], 'M': ['EV/GP Percentile', percent_template], 'N': ['RV Score', percent_template]}

for column in column_formats.keys():
    writer.sheets['Value Strategy'].set_column(f'{column}:{column}', 25, column_formats[column][1])
    writer.sheets['Value Strategy'].writer(f'{column}1', column_formats[column][0], column_formats[column][1])

# Saving Our Excel Output
writer.save()
