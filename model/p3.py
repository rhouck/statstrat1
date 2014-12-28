import math

from p2 import *

def calcualate_portfolio_returns(data, portfolio_weights, test_date):
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
	returns = data / data.shift(1) # - 1
	#returns = (1 + returns)
	
	df = returns[cols] * 1.0
	if short_cols:
		df[short_cols] = df[short_cols] * -1.0

	date_index = [(test_date+datetime.timedelta(days=22))-datetime.timedelta(days=i) for i in range(30)]
	df = df.ix[date_index]
	df = df.dropna(how='any')

	weights = pd.DataFrame(pd.Series(weights, index=cols, name=0))
	portfolio_returns = (df * weights[0]).sum(1)
	portfolio_returns = portfolio_returns.dropna(how='any')
	portfolio_returns = portfolio_returns + 1
	portfolio_daily_index = portfolio_returns.cumprod().dropna(how='any')

	return portfolio_daily_index

def test_performance(data, test_date, look_back_days, return_period_days):
	start_date = test_date - datetime.timedelta(days=look_back_days)
	w = Window(data, start_date=start_date, end_date=test_date, return_period_days=1)
	portfolio = w.get_stat_arb_portfolio(return_period_days=return_period_days)['portfolio_weights']

	portfolio_daily_index = calcualate_portfolio_returns(data, portfolio, test_date)
	bank = {}
	for i in (1, 3, 5, 7, 10):
		returns = (portfolio_daily_index.shift(i) / portfolio_daily_index)
		bank[i] = returns
	performance = pd.DataFrame(data=bank)

	
	selected = None	
	try:
		row = performance.ix[test_date].to_dict()
		for k, v in row.iteritems():
			int(v)
		row['date'] = test_date
		selected = row
	except:
		pass
	
	if not selected:
		print "Could not calculate reurns for %s" % (test_date)

	return selected


def back_test_model(df, start_date, periods, simulation_interval_days, return_period_days, location=""):


	# first find date in dataframe that is closest to chosen start date
	closest = datetime.datetime(1900,1,1,0,0)
	date_index = df.index
	for ind, i in enumerate(date_index):
		#print "%s - %s - %s - %s" % (closest, i, math.fabs((i - start_date).days), math.fabs((closest - start_date).days))
		if math.fabs((i - start_date).days) < math.fabs((closest - start_date).days):
			closest = i
			position = ind

	returns = []
	for i in range(periods):
		try:
			#test_date = start_date + datetime.timedelta(days=(i*simulation_interval_days))
			#test_date = date_index[position] + datetime.timedelta(days=(i*simulation_interval_days))
			test_date = date_index[position+(i*simulation_interval_days)]

			if test_date > datetime.datetime.now():
				raise Exception("test_date cannot be later than current date.")

			print test_date

			portfolio_performance = test_performance(df, test_date, 150, return_period_days)
			if portfolio_performance:
				returns.append(portfolio_performance)
		except:
			pass

	if returns:
		returns = pd.DataFrame.from_records(returns).set_index('date')
		for_csv = returns
		for_csv.to_csv('%smodel_output/test_results.csv' % (location))
		print "Saved simulation output to test_results.csv"

	return returns
	

if __name__ == "__main__":
	
	tix = get_import_io_s_and_p_tickers()
	df = get_collection_as_pandas_df(tix, 'stocks_test', update=False)
	start_date = datetime.datetime(2013,1,7,0,0)
	performance = back_test_model(df, start_date, 130, 5, 7)
	

	
	