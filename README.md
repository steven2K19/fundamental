# fundamental  --- Dataframe for fundamental financials 
It is a Python 3 library for generating stock fundamental data through YahooFinance.
The library is primarily based on yfinance package. fundamental requires only list of tickers input from the user and easily generate dataframe for fundamental ratio analysis, relative value ratio analysis and industry relative analysis.

![github](https://user-images.githubusercontent.com/46503526/72200258-4bddb500-3415-11ea-99b2-cde974a7031f.jpg)

## Data inclusion
- financials for recent 3 years. (income statement, balance sheet, cash flow statement)
- calendar year end financials for comparision.
- TTM financial by aggregate recent 4 quarters data
- Basic share data for each fiscal year end and recent fiscal quarter end
- price data for each fiscal year end and recent fiscal quarter end

## Ticker source example
Holding section show the full list of component
### https://www.ishares.com/us/products/239522/ishares-us-technology-etf


## Usage
```
# https://pypi.org/project/fundamental/
# pip install fundamental

from fundamental import get_df_list

symlist = ['GOOG','MSFT','FB'] 
df = get_df_list(symlist)        

masterdf                  # name of output dataframe

```

## Limitation
- It takes about 10 minutes to create dataframe for 100 stocks. 
- financials are not available from yfinance scraping. 
- slow internet connection would lead scraping error and the program will auto try 3 times. 

