from p3 import *

if __name__ == "__main__":
	"""
	portfolio_returns = pd.io.parsers.read_csv('model_output/test_results.csv', index_col=0, parse_dates=True)

	index_tix = ['^GSPC', '^IXIC']
	index = get_collection_as_pandas_df(index_tix, 'index_test')
	index = index['^GSPC',]
	index_weekly_returns = (index.shift(7) / index)
	index_weekly_returns = index_weekly_returns.ix[portfolio_returns.index]['^GSPC']
	portfolio_returns['index'] = index_weekly_returns

	portfolio_returns_prod = portfolio_returns.cumprod().dropna(how='any')
	"""

	"""
	tix = get_import_io_s_and_p_tickers()	
	end_date = datetime.datetime(2011,7,1,0,0)
	for i in range(5):
		end_date = end_date - datetime.timedelta(days=91*i)
		start_date = end_date - datetime.timedelta(days=91)


		df = get_collection_as_pandas_df(tix, 'stocks_test', update=False)
		w = Window(df, start_date=start_date, end_date=end_date, return_period_days=1)
		w.pull_cointegrated_partners(date_strict=True)
	"""