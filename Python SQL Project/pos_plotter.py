import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from const import *

def pos_plotter(pos:pd.DataFrame, business_line:str, metal:str):
    # enter position for one business_line and one metal (e.g. Prop + Copper)
    pos_ = pos[(pos['business_line'] == business_line) & (pos['metal'] == metal)].copy()

    # add sign of the postion, scale all volume to MT, combine the two
    pos_['sign'] = np.where(pos_['longshort'] == 'L', 1, -1)
    pos_['conv_factor'] = np.where(pos_['unit'] == 'LB', LBS_TO_MT, 1.)
    pos_['sign_volume_mt'] = pos_['sign'] * pos_['volume'] / pos_['conv_factor']
    
    # do plot for each strategy
    strats = pos_['strategy'].unique().tolist()
    
    # create the figure
    fig = plt.figure(figsize=(16, 12))

    for i, strat in enumerate(strats):
        ax = fig.add_subplot(1, len(strats), i+1, projection='3d')
        # select positions associated with specific strategy
        pos_strat = pos_[pos_['strategy'] == strat].reset_index(drop=True)

        # Axis categories
        x_labels =  [d.strftime('%d-%b-%y') for d in sorted(pos_strat['maturity'].unique())]
        y_labels = pos_strat['exchange'].unique().tolist()
        z_values = pos_strat['sign_volume_mt'].tolist()

        # Convert labels to numeric indices
        x_pos = np.arange(len(x_labels))
        y_pos = np.arange(len(y_labels))

        # dx width along x-axis / dy depth along y-axis
        dx=dy=0.125
        
        # Plot each bar
        for i, z in enumerate(z_values):
            # maturity value from the table
            x_val = pos_strat['maturity'].iloc[i].strftime('%d-%b-%y')
            x_label = x_labels.index(x_val)

            # exchange
            y_val = pos_strat['exchange'].iloc[i]
            y_label = y_labels.index(y_val)

            # plot the 3d bar plot
            color = 'green' if z >= 0 else 'red'
            ax.bar3d(x_label, y_label, 0, dx, dy, z, shade=True, color=color)

            # add text
            txt = "{:,}".format(round(z))
            ax.text(x_label*1.05, y_label*0.95, z*1.2, txt, ha='center', va='center', fontsize=fontsize, color='black', bbox=dict(facecolor='white', edgecolor='black', pad=2))

        # Set axis ticks and axis labels
        ax.set_xticks(x_pos + dx/2)
        ax.set_xticklabels(x_labels)
        ax.set_yticks(y_pos+ dy/2)
        ax.set_yticklabels(y_labels)

        # Axis title and main title
        ax.set_zlabel('Volume (MT)',fontsize=fontsize)
        ax.set_xlabel('Maturity',fontsize=fontsize)
        ax.set_ylabel('Exchange',fontsize=fontsize)
        ax.set_title(f'{business_line}-{metal}: {strat}: Qty MT (Maturity vs Exchange)')

        # Center axes and Find midpoints
        x_mid = len(x_labels) / 2 if len(x_labels) != 1 else 0.1
        y_mid = len(y_labels) / 2 if len(y_labels) != 1 else 0.1

        # Compute ranges
        x_range = len(x_labels) + dx/2
        y_range = len(y_labels) + dy/2

        # Set limits so the plot is centered
        ax.set_xlim(x_mid - x_range/2, x_mid + x_range/2)
        ax.set_ylim(y_mid - y_range/2, y_mid + y_range/2)
        plt.tight_layout()

        # Add padding so that Axis Labels do not overlap Tick Labels
        ax.xaxis.labelpad = 15
        ax.yaxis.labelpad = 15
        ax.zaxis.labelpad = 20

        # save figure as png to pos folder
        if not os.path.exists(os.getcwd() + '\\pos'):
            os.makedirs(os.getcwd() + '\\pos') # Check if folder exists if it doesnt create it
        plt.savefig(f"pos\\bl_{business_line}_metal_{metal}_strat_{strat}.png".replace('/','_'), dpi=300, bbox_inches='tight')