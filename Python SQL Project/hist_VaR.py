import pandas as pd
from pathlib import Path
import os

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

import matplotlib.cm as cm
import datetime as dt

from const import *

def hist_VaR(position, 
             hist_price, 
             date,
             agg='business_line',
             look_back_days = 260, 
             confidence=0.99):
    
    # Historical VaR calculation (1-day, 99% confidence, 1-year lookback)
    pos=position.copy()
    
    # Using business_line column as a default column that defines buckets (sets)
    if agg=='business_line':
        # 1. each business line
        pass
    elif agg=='metal':
        # 2. each metal
        pos['business_line'] = 'Metal-' + pos['metal']
    elif agg=='total':
        # 3. for the total portfolio (ie. 3 business lines combined)
        pos['business_line'] = 'total'
    
    # create end date and start date
    date_dt = pd.to_datetime(date)
    start_date_dt = date_dt-pd.Timedelta(days=look_back_days/5*7)

    # create a range of 260 business days ending at start_date
    dates_dt = pd.bdate_range(end=date_dt, periods=look_back_days)[:-1]

    # create id for curve that is 3d tuple (metal, exchange, maturity)
    hist_price['id'] =  hist_price['metal'].astype(str).str.strip()  + '->' + \
                        hist_price['exchange'].astype(str).str.strip()  + '->' + \
                        hist_price['maturity'].astype(str).str.strip()
    
    # save figure as png to pos folde; Check if folder exists if it doesnt create it
    if not os.path.exists(os.getcwd() + '\\var'):
        os.makedirs(os.getcwd() + '\\var') 
    
    # save VaR results
    VaRs = {}
    
    # calculate VaR for each bl
    for bl in pos['business_line'].unique():
        # select one business line (bl)
        pos_bl = pos[pos['business_line']==bl]

        # add sign of the postion, scale all volume to MT, combine the two
        pos_bl['sign'] = np.where(pos_bl['longshort'] == 'L', 1, -1)
        pos_bl['conv_factor'] = np.where(pos_bl['unit'] == 'LB', LBS_TO_MT, 1.)
        pos_bl['sign_volume'] = pos_bl['sign'] * pos_bl['volume']

        # group by metal, exchange, maturity for signed volume
        pos_bl = pos_bl[['metal', 'exchange', 'maturity', 'sign_volume']].groupby(['metal', 'exchange', 'maturity']).sum().reset_index()

        # create a unique id for the 3d tuple
        pos_bl['id'] =  pos_bl['metal'].astype(str).str.strip()  + '->' + \
                        pos_bl['exchange'].astype(str).str.strip()  + '->' + \
                        pos_bl['maturity'].astype(str).str.strip()

        # keep only the id and signed volume (position)
        pos_bl = pos_bl[['id', 'sign_volume']]

        # take only price relevant to positions
        px_bl = hist_price[['price_date', 'quotevalue', 'id']]
        px_bl = px_bl[px_bl['id'].isin(pos_bl['id'].unique())].reset_index(drop=True)

        # for every id (metal, exchange, maturity) create time-series
        id_2_ts = {}

        # for each metal, exchange, maturity calculate simple return (this can extend easily to log return)
        for i in pos_bl['id'].unique():
            # create time-series with specific IDs and just two columns - price date & price value
            ts = px_bl[px_bl['id'] == i][['price_date', 'quotevalue']].reset_index(drop=True)

            # cut thre requested time window that is of interest for VaR
            ts = ts[(ts['price_date'] >= start_date_dt) & (ts['price_date'] < date_dt)]\
                    .sort_values(by='price_date').tail(look_back_days).reset_index(drop=True)
            
            # in case the data is not in the timeframe of [date-lookBackDays, date] that means we do not any data point
            if ts.empty:
                print(f'Not a single data point detected for id {id} for date {date} across look back days {look_back_days}.')
                ts = [0] * look_back_days
            else:
                if (ts.shape[0] < look_back_days): # (if there is less fill-in with constat value)
                    # number of missing rows
                    missing = look_back_days - ts.shape[0]

                    # take the first row and repeat it
                    filler = [ts['quotevalue'].iloc[0]] * missing

                    # concat filler above the original df
                    ts = filler + ts['quotevalue'].tolist()
                else:
                    ts = ts['quotevalue'].tolist()
            
            # save the time-series of prices that is relevant to the id
            id_2_ts[i] = ts
        
        # Here time series is for sure the length of look_back_days; calculate simple return and multiply with position
        Daily_MTM = pd.DataFrame(id_2_ts).diff().dropna().reset_index(drop=True) # simple MTM diff ($/MT)

        # Using Daily MTM Price change multiply with volume to get PL
        PL = pd.DataFrame({i : Daily_MTM[i] * pos_bl[pos_bl['id']==i]['sign_volume'].iloc[0] for i in pos_bl['id'].unique()})

        # Add PnL across all IDs to get total PnL time-series
        PL = PL.sum(axis=1)

        # Calucate historical VaR (Compute the q-th percentile)
        VaR_historical = np.percentile(PL, 100 * (1 - confidence))
        
        # Save VaR
        VaRs[bl] = [VaR_historical]

        # Output print if needed
        # print(f"For BL {bl} 1-Day Historical VaR ({confidence*100:.0f}% confidence level) on {date_dt.strftime('%d-%b-%y')} with {look_back_days} look back days: \n {VaR_historical:,.0f} USD.")
        
        # Create PL graph
        plt.figure(figsize=(10, 6))
        plt.plot(dates_dt, PL)
        plt.axhline(y=VaR_historical, color='red', linestyle='--', linewidth=2, label=f'VaR ({confidence*100:.0f}% conf. lvl.): {VaR_historical:,.0f}')
        plt.title(f'Time-series of Daily PL for BL {bl}')
        plt.xlabel('Data point')
        plt.ylabel('Daily PnL (USD)')
        plt.legend()
        plt.grid()
        plt.savefig(f"var\\BL_{bl}_PL.png".replace('/','_'), dpi=300, bbox_inches='tight')

        # Plot the historical returns and VaR threshold
        plt.figure(figsize=(10, 6))
        plt.hist(PL, bins=50, alpha=0.75, color='blue', edgecolor='black') # density=True
        plt.axvline(VaR_historical, color='red', linestyle='--', label=f'VaR ({confidence*100:.0f}% conf. lvl.): {VaR_historical:,.0f}')
        plt.title(f'Historical Distribution of PL for BL {bl}')
        plt.xlabel('Daily PnL (USD)')
        plt.ylabel('Frequency')
        plt.legend()
        plt.grid()
        plt.savefig(f"var\\BL_{bl}_PL_dist.png".replace('/','_'), dpi=300, bbox_inches='tight')

    return pd.DataFrame(VaRs)
