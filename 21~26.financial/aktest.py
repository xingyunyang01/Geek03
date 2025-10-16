import akshare as ak

stock_zcfz_em_df = ak.stock_zcfz_em(date="20240331")
print(stock_zcfz_em_df)
stock_zcfz_em_df.to_csv("stock_zcfz_em_df.csv", index=False)
