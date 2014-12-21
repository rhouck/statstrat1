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
	end_date = datetime.datetime(2008,10,1,0,0)
	for i in range(5):
		end_date = end_date - datetime.timedelta(days=91*i)
		start_date = end_date - datetime.timedelta(days=91)
		#print end_date
		#print start_date
		
		df = get_collection_as_pandas_df(tix, 'stocks_test', update=False)
		w = Window(df, start_date=start_date, end_date=end_date, return_period_days=1)
		w.pull_cointegrated_partners(date_strict=True)
	"""
		
	tix = get_import_io_s_and_p_tickers()
	df = get_collection_as_pandas_df(tix, 'stocks_test', update=False)
	w = Window(df, start_date=datetime.datetime(2014,7,1,0,0), end_date=datetime.datetime(2014,10,1,0,0), return_period_days=1)
	portfolio = w.get_stat_arb_portfolio(return_period_days=7)
	
	period_returns = (w.daily_index / w.daily_index.shift(7)).tail(1) - 1

	rows = {}
	for i in ('long', 'short'):
	    rows[i] = []
	    for k, v in portfolio['portfolio_weights'][i].iteritems():

	        temp = {}
	        temp['ticker'] = k
	        temp['weight'] = v
	        temp['score'] = -1. * portfolio['performance_chart'][portfolio['performance_chart']['tickers'] == k]['over_performance'].values[0]
	        temp['returns'] = period_returns[k].values[0]
	        temp['pairs'] = [p for p in w.get_cointegrated_beta_list(k, portfolio['pairs'], portfolio['beta_list']).iterkeys()] 
	        rows[i].append(temp)
	
	for i in ('long', 'short'):
		df = pd.DataFrame.from_records(rows[i], columns=[k for k in rows[i][0].iterkeys()])
		ascending = False if i == 'long' else True
		df = df.sort(columns=['score'], ascending=ascending)
		df.to_csv('model_output/%s_picks.csv' % (i))
 