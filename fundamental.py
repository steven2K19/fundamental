import yfinance as yf
from datetime import date, datetime, timedelta
from pandas.tseries.offsets import BDay
import pandas_market_calendars as mcal
import pandas as pd
import numpy as np
import requests
from lxml import html
import ssl


def get_df_list(sym):
    def get_page(url):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                      'application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Pragma': 'no-cache',
            'Referrer': 'https://google.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/77.0.3865.120 Safari/537.36 '
        }
        return requests.get(url, headers=headers)

    def parse_rows(table_rows):
        parsed_rows = []
        for table_row in table_rows:  # iterate  all rows in the table  of <div class="D(tbr)>
            parsed_row = []
            el = table_row.xpath("./div")  # tree.xpath("./div"),   create a list of div  rows
            none_count = 0
            for rs in el:  # iterrate all span  in each row
                try:
                    (text,) = rs.xpath('.//span/text()[1]')
                    parsed_row.append(text)
                except ValueError:
                    parsed_row.append(np.NaN)
                    none_count += 1
            if none_count < 4:  # none_count = 5 dates, then no values for the row
                parsed_rows.append(parsed_row)
        return pd.DataFrame(parsed_rows)

    def clean_data(df):
        df = df.set_index(0)
        df = df.transpose()
        cols = list(df.columns)
        cols[0] = 'Date'  # rename Breakdown col to Date
        df = df.set_axis(cols, axis='columns', inplace=False)  # update cols names
        numeric_columns = list(df.columns)[1::]  # all col except date col
        try:
            for column_name in numeric_columns:
                df[column_name] = df[column_name].str.replace(',', '')  # Remove the thousands separator
                df[column_name] = df[column_name].astype(np.float64)  # Convert the column to float
        except AttributeError:
            pass
        return df

    def scrape_table(url):
        page = get_page(url)
        tree = html.fromstring(page.content)  # page in tree structure,  XPath or CSSSelect;
        table_rows = tree.xpath(
            "//div[contains(@class, 'D(tbr)')]")
        assert len(table_rows) > 0  # ensure rows are found or nothing
        df = parse_rows(table_rows)
        df = clean_data(df)
        return df

    def get_df(symbol):
        # fiscal year financial
        stock = yf.Ticker(symbol)
        dff = stock.financials
        dfb = stock.balancesheet
        dfc = stock.cashflow
        df0 = pd.concat([dff, dfb, dfc], axis=0, sort=False) / 10 ** 6
        df0 = df0.transpose()
        # earning and eps in financial
        url_is = "https://finance.yahoo.com/quote/{0}/financials?p={0}".format(symbol)
        dfe = scrape_table(url_is)
        sharelist = list(dfe['Basic'].dropna())
        idx0 = df0.index
        df1 = df0.reset_index(drop=True)
        df1['Basic'] = pd.Series(sharelist)
        df1 = df1.set_index(idx0).sort_index(axis=0)
        # calendar year financial
        ly = dff.columns.values[0].astype('M8[D]').astype('O')
        lyy1 = int(ly.strftime('%Y%m%d'))
        lyy2 = ly.year * 10 ** 4 + 12 * 10 ** 2 + 20
        if lyy1 > lyy2:
            ly1 = ly.year
            dly1 = df1.iloc[-1]
            dly2 = df1.iloc[-2]
            dly3 = df1.iloc[-3]
        else:
            ly1 = ly.year - 1
            lys = str(ly.year) + '01' + '01'
            lys = date(year=int(lys[0:4]), month=int(lys[4:6]), day=int(lys[6:8]))
            perc = (ly - lys).days + 1
            perc = perc / 365
            dly1 = df1.iloc[-1] * (1 - perc) + df1.iloc[-2] * perc
            dly2 = df1.iloc[-2] * (1 - perc) + df1.iloc[-3] * perc
            dly3 = df1.iloc[-3] * (1 - perc) + df1.iloc[0] * perc
        ly2 = ly1 - 1
        ly3 = ly1 - 2
        lyidx = [ly3, ly2, ly1]
        dcy = pd.concat([dly3, dly2, dly1], axis=1)
        dcy.columns = lyidx
        dcy = dcy.transpose()
        df1 = pd.concat([df1, dcy], axis=0, sort=False)

        # TTM financial
        lastfiscalquarter = stock.quarterly_balancesheet.columns.values[0].astype('M8[D]').astype('O')
        dffttm = stock.quarterly_financials.sum(axis=1)
        dfbttm = stock.quarterly_balancesheet[lastfiscalquarter]
        dfcttm = stock.quarterly_cashflow.sum(axis=1)
        dfttm0 = pd.concat([dffttm, dfbttm, dfcttm])
        dfttm1 = dfttm0.replace({0: np.nan}) / 10 ** 6
        dfttm1 = pd.DataFrame(dfttm1, columns=['TTM'])
        dfttm1 = dfttm1.transpose()
        try:
            dfttm1['Basic'] = float(stock.info['sharesOutstanding'])/10**3
        except KeyError:
            pass
        # combine year and TTM financial:     remove duplicate cols, share cols, addup index, concat
        idx1 = df1.index
        idx2 = dfttm1.index
        idx = idx1.append(idx2)
        _, i = np.unique(df1.columns, return_index=True)
        df1 = df1.iloc[:, i]
        _, i = np.unique(dfttm1.columns, return_index=True)
        dfttm1 = dfttm1.iloc[:, i]
        col_list1 = df1.columns.tolist()
        col_list2 = dfttm1.columns.tolist()
        for co1 in col_list1:
            if co1 not in col_list2:
                dfttm1[co1] = np.nan
        for co2 in col_list2:
            if co2 not in col_list1:
                df1[co2] = np.nan
        col_list1 = df1.columns.tolist()
        col_list1.sort()
        df1 = df1[col_list1]
        col_list2 = dfttm1.columns.tolist()
        col_list2.sort()
        dfttm1 = dfttm1[col_list2]
        df = pd.concat([df1, dfttm1])
        df = df.set_index(idx)
        df['ticker'] = symbol

        # price data   ------- need trade day calendar
        lastfye = dff.columns.values[0].astype('M8[D]').astype('O')
        end = lastfiscalquarter + timedelta(days=5)
        start = lastfye - timedelta(days=365 * 3 + 5)
        ohlc = stock.history(start=start, end=end)
        l4y = str((lastfye - timedelta(days=365 * 3) + pd.tseries.offsets.BusinessDay(n=1)).date().strftime('%Y-%m-%d'))
        l3y = str((lastfye - timedelta(days=365 * 2) + pd.tseries.offsets.BusinessDay(n=1)).date().strftime('%Y-%m-%d'))
        l2y = str((lastfye - timedelta(days=365) + pd.tseries.offsets.BusinessDay(n=1)).date().strftime('%Y-%m-%d'))
        l1y = str((lastfye + pd.tseries.offsets.BusinessDay(n=1)).date().strftime('%Y-%m-%d'))
        lye3 = str(ly1 - 1) + '01' + '01'  # ly1 from calendar year financial
        lye3 = date(year=int(lye3[0:4]), month=int(lye3[4:6]), day=int(lye3[6:8]))
        lye3 = str((lye3 - pd.tseries.offsets.BusinessDay(n=1)).date().strftime('%Y-%m-%d'))
        lye2 = str(ly1) + '01' + '01'
        lye2 = date(year=int(lye2[0:4]), month=int(lye2[4:6]), day=int(lye2[6:8]))
        lye2 = str((lye2 - pd.tseries.offsets.BusinessDay(n=1)).date().strftime('%Y-%m-%d'))
        lye1 = str(ly1 + 1) + '01' + '01'
        lye1 = date(year=int(lye1[0:4]), month=int(lye1[4:6]), day=int(lye1[6:8]))
        lye1 = str((lye1 - pd.tseries.offsets.BusinessDay(n=1)).date().strftime('%Y-%m-%d'))
        nyse = mcal.get_calendar('NYSE')  # print(mcal.get_calendar_names())  available exchange
        nyse = nyse.schedule(start_date=start, end_date=end)
        nyse = list(mcal.date_range(nyse, frequency='1D'))
        days = []
        for t in nyse:
            t = str(t.date())
            days.append(t)

        def tradeday(i):
            if i not in days:
                i = datetime.strptime(i, '%Y-%m-%d').date()
                i = (i + pd.tseries.offsets.BusinessDay(n=1)).date()
                i = str(i)
            return i

        l4y = tradeday(l4y)
        l3y = tradeday(l3y)
        l2y = tradeday(l2y)
        l1y = tradeday(l1y)
        lye3 = tradeday(lye3)
        lye2 = tradeday(lye2)
        lye1 = tradeday(lye1)
        try:
            p_l4y = ohlc.Close.loc[l4y]
            p_l3y = ohlc.Close.loc[l3y]
            p_l2y = ohlc.Close.loc[l2y]
            p_l1y = ohlc.Close.loc[l1y]
            p_lye3 = ohlc.Close.loc[lye3]
            p_lye2 = ohlc.Close.loc[lye2]
            p_lye1 = ohlc.Close.loc[lye1]
            p_l1q = stock.info['previousClose']
            plist = [p_l4y, p_l3y, p_l2y, p_l1y, p_lye3, p_lye2, p_lye1, p_l1q]
            df['price'] = plist
        except KeyError:
            pass
        return df

    def concat_df(df1, df2):
        col_list1 = df1.columns.tolist()
        col_list2 = df2.columns.tolist()
        for co1 in col_list1:
            if co1 not in col_list2:
                df2[co1] = np.nan
        for co2 in col_list2:
            if co2 not in col_list1:
                df1[co2] = np.nan
        col_list1 = df1.columns.tolist()
        col_list1.sort()
        df1 = df1[col_list1]
        col_list2 = df2.columns.tolist()
        col_list2.sort()
        df2 = df2[col_list2]
        df = pd.concat([df1, df2])
        return df

    masterdf = get_df('MSFT')
    erroritem1 = []
    erroritem2 = []
    for item in sym:
        try:
            tempdf = get_df(item)
            masterdf = concat_df(masterdf, tempdf)
            print(item)
        except KeyError:
            print('KeyError: ' + item)
            pass
        except AttributeError:
            print('AttributeError: ' + item)
            pass
        except AssertionError:
            print('AssertionError: ' + item)
            erroritem1.append(item)
            pass
        except ssl.SSLError:
            erroritem1.append(item)
            print('SSLError: ' + item)
            pass

    for item in erroritem1:
        try:
            tempdf = get_df(item)
            masterdf = concat_df(masterdf, tempdf)
            print(item)
        except AssertionError:
            print('AssertionError: ' + item)
            erroritem2.append(item)
            pass
        except ssl.SSLError:
            erroritem2.append(item)
            print('SSLError: ' + item)
            pass
    for item in erroritem2:
        try:
            tempdf = get_df(item)
            masterdf = concat_df(masterdf, tempdf)
            print(item)
        except AssertionError:
            print('AssertionError: ' + item)
            pass
        except ssl.SSLError:
            print('SSLError: ' + item)
            pass
    return masterdf
