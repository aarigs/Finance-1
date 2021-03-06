"""MLT: Utility code.

Acknowldgements to the original code provided by Tucker Balch for the 
Machine Learning For Trading Course offered at Georgia Tech.

This code has been changed significantly and is used for testing the
value of individual and lists of machine learning algorithms.
"""

import os
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def symbol_to_path(symbol, base_dir=os.path.join("", "data")):
    """Return CSV file path given ticker symbol."""
    return os.path.join(base_dir, "{}.csv".format(str(symbol)))


def get_data(symbols, dates, addSPY=True, vol=False):
    """Read stock data (adjusted close) for given symbols from CSV files."""
    df = pd.DataFrame(index=dates)
    if addSPY and 'SPY' not in symbols:  # add SPY for reference, if absent
        symbols = ['SPY'] + symbols

    for symbol in symbols:
        if vol:
            df_temp = pd.read_csv(symbol_to_path(symbol), index_col='Date',
                    parse_dates=True, usecols=['Date', 'Volume'], na_values=['nan'])
            df_temp = df_temp.rename(columns={'Volume': 'Volume_'+symbol})
        else:
            df_temp = pd.read_csv(symbol_to_path(symbol), index_col='Date',
                    parse_dates=True, usecols=['Date', 'Adj Close'], na_values=['nan'])
            df_temp = df_temp.rename(columns={'Adj Close': symbol})
        df = df.join(df_temp)
        if symbol == 'SPY':  # drop dates SPY did not trade
            df = df.dropna(subset=["SPY"])

    return df


def plot_data(df, title="Stock prices", xlabel="Date", ylabel="Price", filename=None):
    """Plot stock prices with a custom title and meaningful axis labels."""
    ax = df.plot(title=title, fontsize=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    if filename is not None:
        plt.savefig(filename)
        
    plt.show()

def calculate_returns(dframe, horizon):
    """Calculate returns on a dataframe fo prices."""
    returns = dframe.shift(-horizon)/dframe - 1
    returns = returns.dropna()
    return returns

def create_training_data(symbol, 
                         start_date = None, 
                         end_date = None,
                         horizon = 5, # Num. days ahead to predict
                         filename = "simData/example.csv", #Save location
                         use_web = False, #Use the web to gether Adjusted Close data?
                         use_vol = False, #Use the volume of stocks traded that day?
                         use_prices = False, #Use future Adj. Close as opposed to future returns
                         direction = False, #Use the direction of the market returns as output
                         indicators = ['Bollinger',
                                       'Momentum',
                                       'Volatility',
                                       'SimpleMA',
                                       'ExponentialMA',
                                       'Lagging',
                                       'Weekdays'],
                        num_lag = 20,
                        check_correlations=False
                         ):
    
        """Retrieve historical data based off start and end dates for selected symbol.
Create and store a training dataframe:
        Features - adj close
                   indicators from indicator list
        Prediction - Future return or
                     Future Adj. Close
"""
        if not end_date or not start_date:
			end_date = dt.date.today()
			year = dt.timedelta(days=365)
			start_date = end_date - year
			
        if use_web:
                import pandas_datareader.data as web
                adj_close = web.DataReader(name=symbol, data_source='yahoo', start=start_date, end=end_date)
                adj_close = pd.DataFrame(adj_close["Adj Close"])
                adj_close.columns = [symbol]
        else:
                dates = pd.date_range(start_date, end_date)
                adj_close = get_data([symbol], dates, False, vol=False)

        # Fill any missing data
        adj_close = adj_close.ffill()
        adj_close = adj_close.bfill()
        df1 = adj_close

        # Add trade volume data to training data
        if use_vol:
                vol = get_data([symbol], dates, False, vol=use_vol)
                vol = vol.fillna(0.0)
                df1 = adj_close.join(vol)

        # Add Indicators from List provided by user
        indicator_list = []
        if "Bollinger" in indicators:
            # Add Bollinger value as indicator
            from indicators.Bollinger import Bollinger
            indicator_list.append(Bollinger())
        if "Momentum" in indicators:
            # Add Momentum value as indicator
            from indicators.Momentum import Momentum
            indicator_list.append(Momentum())
        if "Volatility" in indicators:
            # Add Volatility value as indicator
            from indicators.Volatility import Volatility
            indicator_list.append(Volatility())
        if "SimpleMA" in indicators:
            # Add Simple moving average value as indicator
            from indicators.SimpleMA import SimpleMA
            indicator_list.append(SimpleMA())
        if "ExponentialMA" in indicators:
            # Add exponential moving average value as indicator
            from indicators.ExponentialMA import ExponentialMA
            indicator_list.append(ExponentialMA())
        if "Lagging" in indicators:
            # Add Lagging values as indicators
            from indicators.Lagging import Lag
            for i in range(1,num_lag+1):
                lag = Lag(i)
                lag.addEvidence(adj_close)
                lag_values = lag.getIndicator()
                df1 = df1.join(lag_values)
        if "Weekdays" in indicators:
        	# Add weekdays as indicators
            from indicators.Weekdays import Weekdays
            indicator_list.append(Weekdays())
        
        for indicator in indicator_list:
            indicator.addEvidence(adj_close)
            ind_values = indicator.getIndicator()
            df1 = df1.join(ind_values)
                
        # Add output column ***(output should be returns, not prices)***
        if not use_prices:
            returns = calculate_returns(adj_close[[symbol]],horizon)
            if direction:
                returns[returns.values>0.0] = 1.0
                returns[returns.values<=0.0] = 0.0
        else:
            returns = adj_close[[symbol]].shift(-horizon)
        returns.columns = ["Returns_"+symbol]
        df1 = df1.join(returns)

        # Drop rows without information (ie. NaN for Lagging Indicators)
        df1 = df1.dropna()
        ind_names = [col for col in df1.columns
                       if not col.startswith("Lag") and not col.startswith("Returns")]
        
        # Check correlations between Input features and output
        if check_correlations:
			for name in ind_names:
				print "{}\t".format(name), np.corrcoef(df1[name],
								  df1["Returns_"+symbol])[0][1]
			if "Lagging" in indicators:
				for i in range(1,num_lag+1):
					print "Lag {}\t".format(i), np.corrcoef(df1["Lag{}_".format(i) + symbol],
									  df1["Returns_"+symbol])[0][1]
        # Write csv to simData folder so learners can be tested on the financial data
        df1.to_csv(filename, index_label="Date")

def test_create_training_data():
    start_date = dt.datetime(2004,1,1)
    end_date = dt.datetime(2006,1,1)
    symbol = 'IBM'
    
    create_training_data(
                symbol,
                start_date,
                end_date,
                use_web=True,
                use_prices=True,
                direction=False,
                num_lag=2
                )

if __name__ == "__main__":
    test_create_training_data()
