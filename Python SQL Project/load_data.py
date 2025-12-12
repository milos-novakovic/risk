import pandas as pd
import yaml
from pathlib import Path
from const import *
from standardize_data import standardize_data

def load_data(path: str = "absolute_project_folder_path", business_lines: list = ['pos_copper', 'pos_prop', 'pos_zinclead']):
    # Load YAML absolute project folder path
    with open("config.yml", "r") as f:
        config = yaml.safe_load(f)
    
    # Get path as string
    project_path = Path(config[path])
    
    # If project path exists extract position data and price data
    if project_path.exists():

        # Extract data from business lines, if they exist
        pos: list = []
        for business_line in business_lines:
            if Path(config[business_line]).exists():

                # Load each business line as df in a list to concat later
                pos.append(pd.read_csv(Path(config[business_line])))
                pos[-1].attrs['name'] = f"Postion (BL {business_line})"
                standardize_data(df=pos[-1], 
                                 numeric_col_names = ['volume'], 
                                 date_col_names=['maturity'],
                                 trim_col_names= ['contracttype', 'business_line', 'strategy', 'metal', 'exchange', 'currency', 'longshort', 'unit'])
        
        # Combine all position datasets into one unified table
        pos_df:pd.DataFrame = pd.concat(pos, ignore_index=True)
        
        # Load Historical Price Data, if it exists
        if Path(config['hist_price']).exists():
            hist_price = pd.read_csv(Path(config['hist_price']))
            hist_price.attrs['name'] = "Historical Prices"
            standardize_data(df=hist_price, 
                             numeric_col_names = ['quotevalue'],
                             date_col_names=['price_date', 'maturity'],
                             trim_col_names=['metal', 'exchange', 'unit'])
    else:
        print(f"Path {path} does not exist, please enter correct path.")

    return pos_df, hist_price