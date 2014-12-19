from p2 import *



if __name__ == "__main__":
	
	tix = get_import_io_s_and_p_tickers()
	df = get_collection_as_pandas_df(tix, 'stocks_test', update=False)
	w = Window(df, start_date=datetime.datetime(2014,6,1,0,0), end_date=datetime.datetime(2014,9,1,0,0), return_period_days=1)
	w.get_stat_arb_portfolio(return_period_days=7)	
