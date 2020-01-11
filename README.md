# fundamental
It is a Python 3 library for generating stock fundamental data through YahooFinance.
The library is primarily based on yfinance package. fundamental requires only list of tickers input from the user and easily generate dataframe for fundamental ratio analysis, relative value ratio analysis and industry relative analysis.

## Data inclusion
a. financials for recent 3 years. (income statement, balance sheet, cash flow statement)
b. calendar year end financials for comparision.
c. TTM financial by aggregate recent 4 quarters data
d. Basic share data for each fiscal year end and recent fiscal quarter end
e. price data for each fiscal year end and recent fiscal quarter end

## Ticker Source example
https://www.ishares.com/us/products/239522/ishares-us-technology-etf
Holding section show the full list of component

## usage
```
get_df_list(symlist)
masterdf   # dataframe output

```

## Limitation
a. financials are not available from yfinance scraping. 
b. slow internet connection would lead scraping error and the program will auto try 3 times. 