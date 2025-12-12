import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm

from const import *
def price_outlier_detector(prices:pd.DataFrame):
    # check if there are any NaN values
    if prices.isna().any().any():
        print(f"There are NaN values in prices time series.")

    for metal in prices['metal'].unique():
        for exchange in prices[prices['metal'] == metal]['exchange'].unique():

            #################
            # Prices figure #
            #################

            # Filter out prices
            px = prices[(prices['metal'] == metal) & (prices['exchange'] == exchange)]

            # Get the Unit of Measure (UOM)
            uom = px['unit'].unique()
            if len(uom) == 1:
                uom = uom[0]
            else:
                print('There are different UOMs for same curve.')

            # create a figure
            plt.figure(figsize=(12,6))

            # Get a colormap
            colors = cm.Blues(np.linspace(0.4, 1, len(px['maturity'].unique())))  # shades from lighter to darker blue
            for i, maturity in enumerate(px['maturity'].unique()):
                df_m = px[px['maturity'] == maturity].reset_index(drop=True)
                plt.plot(df_m['price_date'], df_m['quotevalue'], label=maturity.strftime('%d-%b-%y'), color=colors[i])
            
            # set title, labels, legend
            plt.title(f"{metal.upper()} Futures Prices on {exchange}")
            plt.xlabel("Date")
            plt.ylabel(f"Price {uom}")
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            plt.grid(True)

            # save figure as png to pos folder
            if not os.path.exists(os.getcwd() + '\\px'):
                os.makedirs(os.getcwd() + '\\px') # Check if folder exists if it doesnt create it
            plt.savefig(f"px\\Exchange_{exchange}_metal_{metal}.png".replace('/','_'), dpi=300, bbox_inches='tight')

            #####################
            # Prices Statistics #
            #####################
            # stats across all maturities
            all_dsc = px['quotevalue'].describe()

            # stats for each maturity
            maturities, maturity_dsc = px['maturity'].unique(), []
            for i, maturity in enumerate(maturities):
                maturity_dsc.append(px[px['maturity'] == maturity].reset_index(drop=True)['quotevalue'].describe())
            maturity_dsc = pd.concat(maturity_dsc,axis=1)
            maturity_dsc.columns = maturities

            # save stats in excel
            with pd.ExcelWriter('px\\px_stats.xlsx') as writer:
                all_dsc.to_excel(writer, sheet_name='all_dsc', index=True)
                maturity_dsc.to_excel(writer, sheet_name='maturity_dsc', index=True)
