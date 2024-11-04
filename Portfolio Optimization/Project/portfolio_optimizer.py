import numpy as np
import pandas as pd
import datetime as dt
import random
import yfinance as yf
import os

PATH = 'E:\\Projects\\Finoobs\\Portfolio Optimization\\Project\\stocks\\'
risk_free_rate = 0.0125

# Load the stock name to ticker mapping
def load_stock_mapping(file_path):
    stock_mapping = pd.read_csv(file_path)
    return dict(zip(stock_mapping['NAME OF COMPANY'], stock_mapping['SYMBOL']))

# def download_stock_data(ticker, start_date, end_date):
#     """Download stock data from Yahoo Finance and save to CSV."""
#     # ticker = [i + ".NS" for i in list_1]
#     df = yf.download(ticker, start=start_date, end=end_date)
#     if not df.empty:
#         df.to_csv(f"{PATH}{ticker}.csv")  # Save to CSV in the specified path
#     return df

def get_df_from_csv(ticker):
    try:
        df = pd.read_csv(PATH + ticker + '.csv', index_col='Date', parse_dates=True)
    except FileNotFoundError:
        pass
    else:
        return df

def merge_df_by_column_name(col_name, sdate, edate, *tickers):
    mult_df = pd.DataFrame()
    sdate = pd.to_datetime(sdate)
    edate = pd.to_datetime(edate)

    for ticker in tickers:
        # Remove .NS for file reading but keep original ticker for column name
        file_name = ticker.replace('.NS', '')
        try:
            df = get_df_from_csv(file_name)
            if df is not None:
                df.index = pd.to_datetime(df.index)
                mask = (df.index >= sdate) & (df.index <= edate)
                # Use original ticker (with .NS) as column name
                mult_df[ticker] = df.loc[mask][col_name]
        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")
    
    return mult_df

def optimize_portfolio(investment_amount, port_list1):
    stock_mapping = load_stock_mapping('E:\\Projects\\Finoobs\\Portfolio Optimization\\Project\\companies.csv')
    
    # Convert stock names to tickers (which already include .NS)
    port_tickers = []
    unmapped_stocks = []
    for name in port_list1:
        if name in stock_mapping:
            port_tickers.append(stock_mapping[name])
        else:
            unmapped_stocks.append(name)
    
    if unmapped_stocks:
        print(f"Warning: Could not find ticker symbols for these stocks: {unmapped_stocks}")
    
    if not port_tickers:
        raise ValueError("No valid tickers found for the provided stock names.")

    port_list = port_tickers  # No need to add .NS as it's already in the mapping
    print(f"Processing these tickers: {port_list}")
    
    num_files_to_select = len(port_list)
    if num_files_to_select == 0:
        raise ValueError("No valid stock tickers to process")
    
    end_date = dt.datetime.now().strftime('%Y-%m-%d')
    
    mult_df = merge_df_by_column_name('Adj Close', '2019-01-01', end_date, *port_list)
    mult_df = mult_df.apply(pd.to_numeric, errors='coerce')

    if mult_df.empty:
        raise ValueError("No data available for the selected stocks")

    returns = np.log(mult_df / mult_df.shift(1))
    
    p_ret = []
    p_vol = []
    p_SR = []
    p_wt = []
    
    for _ in range(10000):
        weights = np.random.random(num_files_to_select)
        weights /= np.sum(weights)
        
        ret = np.sum(weights * returns.mean()) * 252
        vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
        sr = (ret - risk_free_rate) / vol
        
        p_ret.append(ret)
        p_vol.append(vol)
        p_SR.append(sr)
        p_wt.append(weights)

    p_ret = np.array(p_ret)
    p_vol = np.array(p_vol)
    p_SR = np.array(p_SR)
    p_wt = np.array(p_wt)

    optimal_idx = np.argmax(p_SR)
    optimal_weights = p_wt[optimal_idx]

    # Get current prices
    current_prices = {}
    for stock in port_list:
        ticker = yf.Ticker(stock)
        try:
            price = ticker.info.get('currentPrice')
            if price is None or pd.isna(price):
                price = ticker.info.get('regularMarketPrice')
            if price is not None and not pd.isna(price):
                current_prices[stock] = price
            else:
                print(f"Warning: Could not get price for {stock}")
        except Exception as e:
            print(f"Error getting price for {stock}: {str(e)}")
            continue

    if not current_prices:
        raise ValueError("Could not get current prices for any of the selected stocks")

    total_investment = 0
    recommendations = []
    for i, stock in enumerate(port_list):
        if stock in current_prices:
            amount = investment_amount * optimal_weights[i]
            shares = int(amount / current_prices[stock])
            actual_investment = shares * current_prices[stock]
            total_investment += actual_investment
            recommendations.append({
                'stock': stock.replace('.NS', ''),  # Remove .NS for display
                'weight': float(optimal_weights[i]),
                'shares': shares,
                'investment': float(actual_investment)
            })

    if not recommendations:
        raise ValueError("Could not generate recommendations for any of the selected stocks")

    return recommendations, float(p_ret[optimal_idx]), float(p_vol[optimal_idx]), float(total_investment)