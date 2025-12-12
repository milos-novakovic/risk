
from load_data import load_data, pd
from DB_connector import DB_connector
from pos_plotter import pos_plotter
from price_outlier_detector import price_outlier_detector
from hist_VaR import hist_VaR

def main():

    # 1. Load data from CSVs (positions and historical prices)
    pos, hist_price = load_data()

    # 2. Load data in the DB
    DB = DB_connector(pos, hist_price)

    # 3. Plot Strategies
    for bl in pos['business_line'].unique():
        for metal in pos[pos['business_line'] == bl]['metal'].unique():
            pos_plotter(pos=pos,
                        business_line=bl,
                        metal=metal)
    
    # 4. Price Outlier Detecotr
    price_outlier_detector(prices=hist_price)

    # 5. VaR calculator
    date = '2025-09-01'
    look_back_days = 260 
    confidence=0.99
    VaRs = []

    for agg in ['business_line', 'metal', 'total']:
        VaRs.append(hist_VaR(position=pos, 
                             hist_price=hist_price,  
                             date=date, 
                             agg=agg,
                             look_back_days=look_back_days,
                             confidence=confidence))
    VaRs = pd.concat(VaRs,axis=1)
    # save stats in excel
    with pd.ExcelWriter('var\\VaRs.xlsx') as writer:
        VaRs.to_excel(writer, sheet_name='VaR', index=False)

    debug = 0

if __name__ == "__main__":
    main()