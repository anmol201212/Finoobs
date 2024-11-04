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

def download_stock_data(ticker, start_date, end_date):
    """Download stock data from Yahoo Finance and save to CSV."""
    # ticker = [i + ".NS" for i in list_1]
    df = yf.download(ticker, start=start_date, end=end_date)
    if not df.empty:
        df.to_csv(f"{PATH}{ticker}.csv")  # Save to CSV in the specified path
    return df

def get_df_from_csv(ticker):
    """Get DataFrame from CSV, download if not found."""
    # ticker1 = ticker[:-3]
    try:
        df = pd.read_csv(PATH + ticker[:-3] + '.csv', index_col='Date', parse_dates=True)
    except FileNotFoundError:
        print(f"CSV for {ticker} not found. Downloading data...")
        end_date = dt.datetime.now().strftime('%Y-%m-%d')
        df = download_stock_data(ticker, '2019-01-01', end_date)
    return df

def merge_df_by_column_name(col_name, sdate, edate, *tickers):
    """Merge DataFrames for multiple tickers."""
    mult_df = pd.DataFrame()
    sdate = pd.to_datetime(sdate)
    edate = pd.to_datetime(edate)

    for x in tickers:
        df = get_df_from_csv(x)
        if df is not None and not df.empty:
            df.index = pd.to_datetime(df.index)
            mask = (df.index >= sdate) & (df.index <= edate)
            mult_df[x] = df.loc[mask][col_name]

    # Check if mult_df is empty
    if mult_df.empty:
        print("No data retrieved for the selected tickers.")
    
    return mult_df

def optimize_portfolio(investment_amount, port_list):
    
    stock_mapping = load_stock_mapping('E:\\Projects\\Finoobs\\Portfolio Optimization\\Project\\companies.csv')
    
    if not port_list:
        raise ValueError("No stock tickers provided for optimization.")

    # Convert stock names to tickers
    port_tickers = [stock_mapping[name] for name in port_list if name in stock_mapping]
    
    if not port_tickers:
        raise ValueError("No valid tickers found for the provided stock names.")

    end_date = dt.datetime.now().strftime('%Y-%m-%d')
    mult_df = merge_df_by_column_name('Adj Close', '2019-01-01', end_date, *port_tickers)

    if mult_df.empty:
        raise ValueError("The DataFrame is empty. Check the stock tickers and CSV files.")

    mult_df = mult_df.apply(pd.to_numeric, errors='coerce')
    returns = np.log(mult_df / mult_df.shift(1))

    p_ret, p_vol, p_SR, p_wt = [], [], [], []

    print("hehehe",port_tickers)
    
    for _ in range(10000):
        weights = np.random.random(len(port_tickers))
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

    # Get current prices using tickers
    current_prices = {}
    for stock in port_tickers:
        ticker = yf.Ticker(stock)
        current_prices[stock] = ticker.info.get('currentPrice', np.nan)

    total_investment = 0
    recommendations = []
    for i, stock in enumerate(port_tickers):
        amount = investment_amount * optimal_weights[i]
        shares = int(amount / current_prices[stock])
        actual_investment = shares * current_prices[stock]
        total_investment += actual_investment
        recommendations.append({
            'stock': stock,
            'weight': optimal_weights[i],
            'shares': shares,
            'investment': actual_investment
        })

    return recommendations, p_ret[optimal_idx], p_vol[optimal_idx], total_investment
