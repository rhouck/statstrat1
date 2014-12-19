from p2 import *

def calcualate_portfolio_returns(data, portfolio_weights):
	if not isinstance(portfolio_weights, dict):
			raise ValueError("Portfolio_weights must be dictionary")
	if ('long' or 'short') not in portfolio_weights:
		raise KeyError("Portfolio_weights must contain long and short portfolio weight dicts (can be empty)")
	
	cols = []
	weights = []
	for k, v in portfolio_weights['long'].iteritems():
		cols.append(k)
		weights.append(v)
	short_cols = []
	for k, v in portfolio_weights['short'].iteritems():
		short_cols.append(k)
		cols.append(k)
		weights.append(v)

	# convert prices to daily cumulative returns
	# this is helpful when looking into correlations and calculating betas
	returns = data / data.shift(1) - 1
	returns = (1 + returns)
	
	df = returns[cols] - 1
	if short_cols:
		df[short_cols] = df[short_cols] * -1

	weights = pd.DataFrame(pd.Series(weights, index=cols, name=0))
	portfolio_returns = (df * weights[0]).sum(1)
	portfolio_daily_index = portfolio_returns.cumprod()
	return portfolio_daily_index

def test_performance(data, test_date, look_back_days):
	start_date = test_date - datetime.timedelta(days=look_back_days)
	w = Window(data, start_date=start_date, end_date=test_date, return_period_days=1)
	portfolio = w.get_stat_arb_portfolio(return_period_days=7)
	
	portfolio_daily_index = calcualate_portfolio_returns(data, portfolio)
	
	bank = {}
	date_index = [test_date-datetime.timedelta(days=i) for i in range(3)]
	for i in (1, 3, 7, 14):
		returns = (portfolio_daily_index.shift(i) / portfolio_daily_index)
		bank[i] = returns.ix[date_index]
	performance = pd.DataFrame(data=bank)
	return performance
	
if __name__ == "__main__":
	
	tix = get_import_io_s_and_p_tickers()
	df = get_collection_as_pandas_df(tix, 'stocks_test', update=True)
	test_date = datetime.datetime(2014,5,1,0,0)
	print test_performance(df, test_date, 90)
	
