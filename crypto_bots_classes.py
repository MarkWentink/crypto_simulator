import glob
from datetime import datetime
import math
import numpy as np
import pandas as pd

import plotly.express as px
import streamlit as st

import yfinance as yf
yf.pdr_override()
from pandas_datareader import data as wb


class Yahoo_interface():
    '''
    Interface class to process Yahoo Finance API calls. 
    Should be initialised with a list of relevant tokens, and a start date.
    Can return the daily historical prices of a specific token, or the full list of defined tokens, from the given start date to today.
    
    '''
    def __init__(self, tokens, start):
        self.tokens = tokens
        self.last_retrieve_all = start


    def retrieve_all(self, alt_start=None):
        prices = pd.DataFrame()
        if alt_start:
            start_date = alt_start
        else:
            start_date = self.last_retrieve_all

        if start_date == datetime.today().date():
            print('Nothing to retrieve')
            return None

        print('retrieving...')
        for token in self.tokens:
            tok = wb.DataReader(token, start = start_date+pd.DateOffset(1))
            prices[token] = tok['Adj Close']

        self.last_retrieve_all = datetime.today().date()
        prices['USD'] = 1
        return prices


    def retrieve(self, token, since):
        prices = pd.DataFrame()

        print('retrieving')
        tok = wb.DataReader(token, start = since )
        prices[token] = tok['Adj Close']
        prices['USD'] = 1
        return prices
    

class Price_data():
    '''
    dataset object for historical price data. 
    Initialised with a csv filepath. 
    If a file already exists at the filepath, the class can load in the data and/or update the data to today. Alternatively, a new dataset can be generated to overwrite the existing file.
    If no file exists at the filepath, a file can be generated from a given token list and start date.
    '''
    def __init__(self, filepath):
        self.filepath = filepath
        self.prices = None


    def load_prices(self):
        try:
            self.prices = pd.read_csv(self.filepath, header=0)
        except:
            print(f'No data found at {self.filepath}. Check the file path or try generate_data()')
            return -1
        
        if 'Date' not in self.prices.columns:
            raise KeyError('Date not found in columns')
        self.prices['Date'] = pd.to_datetime(self.prices['Date'])
        self.prices = self.prices.set_index('Date')
        self.last_date = self.prices.index[-1].date()
        return self.prices


    def update_data(self):
        if self.prices is None:
            print('Loading prices')
            try:
                self.load_prices()
            except:
                print(f'Could not locate price data at {self.filepath}')
                return -1
        
        self.last_date = self.prices.index[-1].date()

        if self.last_date != datetime.today().date():
            interface = Yahoo_interface(self.prices.columns, self.last_date)
            new_prices = interface.retrieve_all()
            self.prices = pd.concat([self.prices, new_prices])
            self.prices.to_csv(self.filepath, header = True)
        else:
            print('Prices are up to date')

    
    def generate_data(self, token_list, start_date, overwrite=False):

        if not overwrite:
            if self.filepath in glob.glob('*'):
                print(f'{self.filepath} already exists. Use kwarg overwrite=True to overwrite existing files.')
                return -1

        interface = Yahoo_interface(token_list, start_date)
        self.prices = interface.retrieve_all()

        print(f'Writing to filepath: {self.filepath}')
        self.prices.to_csv(self.filepath, header=True)
        

class Portfolio():

    def __init__(self, name, initial_split, start_date, start_value, prices, strategy):

        self.strategy = strategy
        self.start_value = start_value
        self.error_log = {'not enough cash': 0}
        
        assert round(sum(list(initial_split.values())), 2) == 1, 'initial_split must add up to 1'
        self.initial_state = {}

        if 'USD' not in initial_split.keys():
            self.initial_state['USD'] = 0
        
        for token in initial_split.keys():
            self.initial_state[token] = (initial_split[token]*self.start_value)/(prices.loc[start_date, token])


        self.holdings = pd.DataFrame.from_dict({k: [v] for k,v in self.initial_state.items()}) 
        self.holdings.index = pd.date_range(start=start_date, end=start_date)  
        self.values = prices.loc[self.holdings.index, self.holdings.columns] * self.holdings.loc[:, self.holdings.columns]
        self.name = name
        self.hold_duration = {}

    def valuate(self):
        return round(self.values.sum(axis=1).iloc[-1], 2)
    
    def value_history(self):
        return round(self.values.sum(axis=1), 2)
    
    def roi(self):
        annualised = ((self.values.sum(axis=1).iloc[-1] / self.start_value)**(365/len(self.holdings.index))-1)
        return round(annualised*100, 2)
    
    def volatility(self):
        daily_prop_change = (self.value_history() - self.value_history().shift()) / self.value_history().shift()
        return (daily_prop_change*100).std()
    
    def summary(self):
        print(f'Start value:   {self.start_value}\n'
              f'Current value: {self.valuate()}\n'
              f'Total return:  {self.valuate() - self.start_value}\n'
              f'Days held:     {len(self.holdings.index)}\n'
              f'annualised:    {self.roi()} %\n'
              f'Volatility:    {self.volatility()}')
        return 

    def execute_sell(self, coin, date, prices):
        value = math.floor(self.holdings.loc[date, coin]*prices.loc[date, coin]*100)/100.0
        self.holdings.loc[date, 'USD'] += value
        self.holdings.loc[date, coin] = 0
        #print(f'Sold {coin} worth: {value}') 
        self.hold_duration.pop(coin)  
        return

    def execute_buy(self, coin, value, date, prices):
        if value > self.holdings.loc[date, 'USD']:
            #print('Not enough cash available')
            self.error_log['not enough cash'] += 1
            return
        else:
            self.holdings.loc[date, 'USD'] = self.holdings.loc[date, 'USD'] - value
            self.holdings.loc[date, coin] = self.holdings.loc[date, coin] + (value/prices.loc[date, coin])
            #print(f'bought {coin} worth: {value}')
            self.hold_duration[coin] = 0
            return     
    
    def new_simulate_update(self, prices):

        for date in pd.date_range(start=self.holdings.index[-1]+pd.DateOffset(days=1), end=prices.index[-1] ):
            #print(date)
            # new row in holdings table
            self.holdings.loc[date, :] = self.holdings.loc[date-pd.DateOffset(days=1), :]
            # increment hold_durations
            self.hold_duration = {k: v+1 for k,v in self.hold_duration.items()}
            #print(self.hold_duration)
            
            # consult strategy
            # strategy returns list of sell trades as strings 'coin'
            # strategy returns list of buy trades as tuples (coin, value)
            sell_trades, buy_trades = self.strategy.think(self, date, prices)
            # execute trades
            for trade in sell_trades:
                self.execute_sell(trade, date, prices)
            for trade in buy_trades:
                self.execute_buy(*trade, date, prices)

            # new row in values table
            self.values.loc[date, :] = prices.loc[date, self.holdings.columns] * self.holdings.loc[date, :]

        print(self.error_log)


class StrategyHold():

    def __init__(self ):
        return

    def think(self, portfolio, date, prices):
        sell_trades = []
        buy_trades = []
        return sell_trades, buy_trades


class StrategyRules():

    def __init__(self, buy_rule, buy_period, buy_signal, sell_rule, sell_period, exposure):
        self.rules = [(buy_rule, buy_period, buy_signal), (sell_rule, sell_period), exposure]
        self.buy_rule = buy_rule
        self.buy_period = buy_period
        self.buy_signal = buy_signal
        self.sell_rule = sell_rule
        self.sell_period = sell_period
        self.exposure = exposure
        return

    def think(self, portfolio, date, prices):
        
        # selling
        if self.sell_rule == 'hold':
            sell_trades = [coin for coin in portfolio.hold_duration if portfolio.hold_duration[coin] >= self.sell_period]
        
        elif self.sell_rule == 'reversal':
            candidates = [coin for coin in portfolio.holdings.iloc[-1].index if portfolio.holdings.iloc[-1].loc[coin] > 0 and coin != 'USD']
            subset = prices.loc[:, candidates]
            requirements = []
            for i in range(self.sell_period):
                requirements.append(subset.shift(i)<subset.shift(i+1))
                candidates = subset.columns[np.where((sum(requirements) == self.sell_period)
                                                 .loc[portfolio.holdings.index[-1], :])]
            sell_trades = candidates
        # buying
        buy_trades = []
        subset = prices.loc[:, portfolio.holdings.columns.drop('USD')]
        if self.buy_rule == 'consecutive':
            # if up x days and if not already holding
            requirements = []
            for i in range(self.buy_period):
                requirements.append(subset.shift(i)>subset.shift(i+1))
            candidates = subset.columns[np.where((sum(requirements) == self.buy_period)
                                                 .loc[portfolio.holdings.index[-1], :])]

            
        elif self.buy_rule == 'window':
            # if up x amount in y days and not already holding
            candidates = subset.columns[np.where((((subset - subset.shift(self.buy_period))/subset.shift(self.buy_period)) > self.buy_signal)
                                                 .loc[portfolio.holdings.index[-1], :])]
        

        buys = [x for x in candidates if x not in portfolio.hold_duration.keys()]
        if portfolio.holdings.iloc[-1]['USD'] < 1:
            pass
        else:
            if portfolio.holdings.iloc[-1]['USD'] < portfolio.valuate()*self.exposure*len(buys):
                value = math.floor(portfolio.holdings.iloc[-1]['USD'] / len(buys)*100)/100.0 
            else:
                value = math.floor(portfolio.valuate()*self.exposure*100)/100.0
            for coin in buys:           
                buy_trades.append((coin, value))

        return sell_trades, buy_trades


def portfolio_plotter(portfolios):
    '''
    Plots the total value of the given portfolio(s) over time as a lineplot

    inputs
    portfolios: either a portfolio object or list of portfolio objects

    returns
    a plotly lineplot showing the given portfolios' value histories
    '''

    if isinstance(portfolios, list):
        plot_data = pd.DataFrame()
        for portfolio in portfolios:
            plot_data = pd.concat([plot_data, pd.DataFrame(portfolio.value_history(), columns=[portfolio.name])], axis=1)
    else:
        plot_data = pd.DataFrame(portfolios.value_history(), columns=[portfolio.name])
    
    fig = px.line(plot_data )
    fig.update_xaxes(rangeslider_visible = True,
                     rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all")
                        ])
    ))
    fig.update_layout(legend_title_text='Portfolio', width=1000)
    fig.show()
    return 0


@st.cache_data 
def load_data(path):
    '''
    Creates a Price_data object and triggers the update_data method, which confirms the dataset currently in memory is up to date. 
    If not, it triggers an API call to the Yahoo Finance API through pandas_datareader.
    Once prices are updated, they are loaded in and the datetime index is set. 
    '''
    data = Price_data(path)
    data.update_data()
    prices = data.load_prices()
    prices = prices.map(lambda x: round(x, 4 - int(math.floor(math.log10(abs(x))))))
    prices = prices.rename(columns={'UNI7083-USD':'UNI-USD', 'STX4847-USD':'STX-USD'})
    return prices


def load_tokens(path):
    '''
    
    '''
    with open(path) as f:
        token_list = [x.strip() for x in f.readlines()]
        tokens = [x for x in token_list if x not in ['USD', 'USDT-USD', 'USDC-USD', 'DAI-USD', 'SHIB-USD']]
        tokens.remove('UNI7083-USD')
        tokens.remove('STX4847-USD')
        tokens.extend(['UNI-USD', 'STX-USD'])
    return tokens